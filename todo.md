# Project TODO

- [x] Inspect the exact labelled and unlabelled Excel datasets from the supplied archive.
- [x] Document dataset dimensions, columns, dtypes, missing values, duplicates, unique values, text fields, structured fields, and target balance.
- [x] Implement leakage-safe cleaning, deduplication, missing-value handling, text normalization, and stratified train/test splitting.
- [x] Compare text-only, structured-only, and combined feature configurations.
- [x] Train and tune Logistic Regression, Multinomial Naive Bayes, Linear SVM, and a structured baseline where appropriate.
- [x] Calculate accuracy, precision, recall, F1, ROC-AUC, PR-AUC, confusion matrix, and false-negative analysis.
- [x] Select and persist the final preprocessing and model artifacts for reproducible inference.
- [x] Build backend inference and overview endpoints using the persisted model outputs.
- [x] Build an elegant responsive screening dashboard with risk label, confidence, and contributing warning signals.
- [x] Build a data and model overview workspace with coverage, model status, evaluation metrics, and recent sample predictions.
- [x] Add unit tests for preprocessing, prediction explainability, and API-facing model behavior.
- [x] Run type checks, tests, build validation, and responsive visual verification.
- [ ] Save the completed project checkpoint and deliver the project version.

- [x] Implement and record a true combined text-plus-structured feature experiment.
- [x] Add meaningful hyperparameter searches for Logistic Regression, MultinomialNB, and Linear SVM, recording tested ranges and best results.
- [x] Add automated tests for preprocessing/training outputs and tRPC model overview/predict procedures, including invalid-input behavior.
- [x] Expand MultinomialNB tuning to multiple alpha values and persist the full tested parameter ranges.
- [x] Add automated validation for generated overview and portable model bundle structure/content.
