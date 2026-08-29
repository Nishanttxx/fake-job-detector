from pathlib import Path
import json
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT = DATA_DIR / "dataset_inspection.json"

report = {}
for path in sorted(DATA_DIR.glob("*.xlsx")):
    df = pd.read_excel(path)
    info = {
        "file": path.name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": [str(c) for c in df.columns],
        "dtypes": {str(k): str(v) for k, v in df.dtypes.items()},
        "missing_values": {str(k): int(v) for k, v in df.isna().sum().items()},
        "duplicate_rows": int(df.duplicated().sum()),
        "nunique": {str(k): int(v) for k, v in df.nunique(dropna=False).items()},
        "sample": df.head(3).fillna("").astype(str).to_dict(orient="records"),
    }
    target_candidates = []
    for col in df.columns:
        name = str(col).lower()
        nunique = df[col].nunique(dropna=True)
        if any(token in name for token in ("fraud", "fake", "label", "target", "class", "spam")) and nunique <= 10:
            target_candidates.append({"column": str(col), "nunique": int(nunique), "value_counts": {str(k): int(v) for k, v in df[col].value_counts(dropna=False).items()}})
    info["target_candidates"] = target_candidates
    info["numeric_features"] = [str(c) for c in df.select_dtypes(include="number").columns]
    info["categorical_features"] = [str(c) for c in df.select_dtypes(include=["object", "category", "bool"]).columns]
    info["text_features"] = [str(c) for c in df.select_dtypes(include=["object"]).columns if df[c].astype(str).str.len().mean() > 40]
    report[path.name] = info

OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(report, indent=2, ensure_ascii=False))
