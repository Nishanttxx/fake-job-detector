from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, confusion_matrix,
                             f1_score, precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, train_test_split
from scipy.sparse import hstack
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
LABELLED = DATA / "processed_labeled_dataset_without_encoding.xlsx"
UNLABELLED = DATA / "preprocessed_unlabelled_data_bert.xlsx"
RANDOM_STATE = 42
TEXT_COLUMNS = ["job_title", "company_profile", "job_desc", "skills_desc", "salary_range", "employment_type", "text"]
STRUCTURED_COLUMNS = ["location", "industry", "employment_type"]


def clean_text(value: Any) -> str:
    text = "" if pd.isna(value) else str(value)
    text = re.sub(r"<[^>]+>", " ", text.lower())
    text = re.sub(r"https?://\S+|www\.\S+", " urltoken ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def row_text(df: pd.DataFrame) -> pd.Series:
    parts = []
    for col in TEXT_COLUMNS:
        if col in df:
            parts.append(df[col].map(clean_text))
    combined = parts[0].copy()
    for part in parts[1:]:
        combined = combined + " " + part
    return combined.str.replace(r"\s+", " ", regex=True).str.strip()


def metric_block(y_true, y_pred, scores) -> dict[str, Any]:
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist()
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, scores)), 4),
        "pr_auc": round(float(average_precision_score(y_true, scores)), 4),
        "confusion_matrix": cm,
        "false_negatives": int(cm[1][0]),
        "false_positives": int(cm[0][1]),
    }


def main() -> None:
    df = pd.read_excel(LABELLED)
    unlabelled = pd.read_excel(UNLABELLED)
    unlabelled_rows = len(unlabelled)
    unlabelled_duplicate_rows = int(unlabelled.duplicated().sum())
    del unlabelled
    raw_rows = len(df)
    duplicates = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    labelled_rows_before_target = len(df)
    df = df[df["fraudulent"].notna()].copy()
    df["fraudulent"] = df["fraudulent"].astype(int)
    # Keep the source workbook as truth while using a fixed stratified cap for bounded local training.
    if len(df) > 5000:
        df, _ = train_test_split(df, train_size=5000, random_state=RANDOM_STATE, stratify=df["fraudulent"])
        df = df.reset_index(drop=True)
    X_train, X_test, y_train, y_test = train_test_split(
        df, df["fraudulent"], test_size=0.2, random_state=RANDOM_STATE, stratify=df["fraudulent"]
    )

    train_text = row_text(X_train)
    test_text = row_text(X_test)
    vectorizer = TfidfVectorizer(
        lowercase=False, strip_accents="unicode", ngram_range=(1, 2), min_df=2,
        max_df=0.98, max_features=1000, sublinear_tf=True, token_pattern=r"(?u)\b[\w$@.-]{2,}\b"
    )
    Xtr = vectorizer.fit_transform(train_text)
    Xte = vectorizer.transform(test_text)

    results: list[dict[str, Any]] = []
    lr_grid = GridSearchCV(
        LogisticRegression(class_weight="balanced", max_iter=250, solver="liblinear", random_state=RANDOM_STATE),
        {"C": [0.5, 1.0, 2.0]}, cv=2, scoring="f1", n_jobs=1
    )
    lr_grid.fit(Xtr, y_train)
    lr = lr_grid.best_estimator_
    lr_scores = lr.predict_proba(Xte)[:, 1]
    results.append({"model": "Logistic Regression", "features": "TF-IDF text", "best_params": {"C": lr_grid.best_params_["C"], "class_weight": "balanced"}, **metric_block(y_test, (lr_scores >= 0.5).astype(int), lr_scores)})

    nb_grid = GridSearchCV(MultinomialNB(), {"alpha": [0.1, 0.5, 1.0, 2.0]}, cv=2, scoring="f1", n_jobs=1)
    nb_grid.fit(Xtr, y_train)
    nb = nb_grid.best_estimator_
    nb_scores = nb.predict_proba(Xte)[:, 1]
    results.append({"model": "Naive Bayes", "features": "TF-IDF text", "best_params": {"alpha": nb_grid.best_params_["alpha"]}, **metric_block(y_test, (nb_scores >= 0.5).astype(int), nb_scores)})

    svm_grid = GridSearchCV(LinearSVC(class_weight="balanced", random_state=RANDOM_STATE), {"C": [0.25, 1.0, 2.0]}, cv=2, scoring="f1", n_jobs=1)
    svm_grid.fit(Xtr, y_train)
    svm = svm_grid.best_estimator_
    svm_scores = svm.decision_function(Xte)
    results.append({"model": "Linear SVM", "features": "TF-IDF text", "best_params": {"C": svm_grid.best_params_["C"], "class_weight": "balanced"}, **metric_block(y_test, (svm_scores >= 0).astype(int), svm_scores)})

    structured_train = pd.get_dummies(X_train[STRUCTURED_COLUMNS].fillna("missing").astype(str), columns=STRUCTURED_COLUMNS)
    structured_test = pd.get_dummies(X_test[STRUCTURED_COLUMNS].fillna("missing").astype(str), columns=STRUCTURED_COLUMNS).reindex(columns=structured_train.columns, fill_value=0)
    structured_model = LogisticRegression(class_weight="balanced", max_iter=500, solver="liblinear", random_state=RANDOM_STATE)
    structured_model.fit(structured_train, y_train)
    structured_scores = structured_model.predict_proba(structured_test)[:, 1]
    results.append({"model": "Logistic Regression", "features": "Structured only", "best_params": {"C": 1.0, "class_weight": "balanced"}, **metric_block(y_test, (structured_scores >= 0.5).astype(int), structured_scores)})

    # Combined experiment: sparse TF-IDF plus one-hot structured features.
    combined_train = hstack([Xtr, structured_train.astype(float).values]).tocsr()
    combined_test = hstack([Xte, structured_test.astype(float).values]).tocsr()
    combined_grid = GridSearchCV(LogisticRegression(class_weight="balanced", max_iter=300, solver="liblinear", random_state=RANDOM_STATE), {"C": [0.5, 1.0, 2.0]}, cv=2, scoring="f1", n_jobs=1)
    combined_grid.fit(combined_train, y_train)
    combined_model = combined_grid.best_estimator_
    combined_scores = combined_model.predict_proba(combined_test)[:, 1]
    results.append({"model": "Logistic Regression", "features": "TF-IDF + structured", "best_params": {"C": combined_grid.best_params_["C"], "class_weight": "balanced"}, **metric_block(y_test, (combined_scores >= 0.5).astype(int), combined_scores)})

    # Portable bundle: frontend/server can reproduce TF-IDF + logistic score without Python.
    vocab = {str(k): int(v) for k, v in vectorizer.vocabulary_.items()}
    bundle = {
        "version": "2026.08.29",
        "target": "fraudulent",
        "label_map": {"0": "Legitimate", "1": "Fraudulent"},
        "text_columns": TEXT_COLUMNS,
        "vectorizer": {"vocabulary": vocab, "idf": vectorizer.idf_.tolist(), "ngram_range": [1, 2], "max_features": 1000},
        "model": {"name": "Logistic Regression", "features": "Combined normalized posting text", "coef": lr.coef_[0].tolist(), "intercept": float(lr.intercept_[0]), "threshold": 0.5, "best_params": {"C": lr_grid.best_params_["C"], "class_weight": "balanced"}},
        "training": {"random_state": RANDOM_STATE, "raw_rows": raw_rows, "duplicate_rows": duplicates, "rows_after_dedup": labelled_rows_before_target, "labelled_rows": len(df), "training_cap": 5000, "train_rows": len(X_train), "test_rows": len(X_test), "unlabelled_rows": unlabelled_rows, "positive_count": int(df["fraudulent"].sum()), "negative_count": int((df["fraudulent"] == 0).sum())},
        "results": results,
        "tuning": {"logistic_regression": {"C": [0.5, 1.0, 2.0]}, "multinomial_nb": {"alpha": [0.1, 0.5, 1.0, 2.0]}, "linear_svm": {"C": [0.25, 1.0, 2.0]}, "combined_logistic_regression": {"C": [0.5, 1.0, 2.0]}},
        "warning_signals": [
            {"id": "urgency", "label": "Urgent or pressure language", "terms": ["immediate hiring", "urgent", "act now", "quick money", "limited time"], "weight": 0.18},
            {"id": "payment", "label": "Payment or investment request", "terms": ["pay a fee", "upfront payment", "investment required", "wire transfer", "gift card"], "weight": 0.32},
            {"id": "contact", "label": "Unusual contact details", "terms": ["send resume to", "gmailcom", "whatsapp", "telegram", "contact now"], "weight": 0.16},
            {"id": "salary", "label": "Unusually high compensation cues", "terms": ["5000week", "$5000", "earn 5000", "no experience high pay", "guaranteed income"], "weight": 0.2},
            {"id": "low_barrier", "label": "Low-barrier hiring promise", "terms": ["no degree required", "no experience required", "work from home", "flexible hours"], "weight": 0.1},
        ],
    }
    (ARTIFACTS / "model_bundle.json").write_text(json.dumps(bundle), encoding="utf-8")
    joblib.dump({"vectorizer": vectorizer, "model": lr}, ARTIFACTS / "model_bundle.joblib")
    overview = {
        "source_files": [LABELLED.name, UNLABELLED.name],
        "labelled_schema": {"columns": [str(c) for c in df.columns], "dtypes": {str(k): str(v) for k, v in df.dtypes.items()}, "missing_values": {str(k): int(v) for k, v in pd.read_excel(LABELLED).isna().sum().items()}, "duplicate_rows": duplicates},
        "unlabelled_schema": {"rows": unlabelled_rows, "duplicate_rows": unlabelled_duplicate_rows},
        "training": bundle["training"], "tuning": bundle["tuning"], "results": results, "selected_model": results[0], "decisions": ["Removed exact duplicate rows before splitting.", "Excluded rows with missing fraudulent labels from supervised training.", "Kept text markers such as salary, email-like contact strings, urgency, and payment language because they can carry fraud signal.", "Fitted TF-IDF only on the training split to prevent leakage.", "Used class-balanced linear models because the positive class is smaller than the legitimate class."],
    }
    (ARTIFACTS / "overview.json").write_text(json.dumps(overview, indent=2), encoding="utf-8")
    print(json.dumps(overview, indent=2))


if __name__ == "__main__":
    main()
