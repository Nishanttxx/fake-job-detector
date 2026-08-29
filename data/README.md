# Supplied dataset notes

This project uses the exact Excel workbooks supplied with the task. The labelled source is `processed_labeled_dataset_without_encoding.xlsx`; the unlabelled source is `preprocessed_unlabelled_data_bert.xlsx`. No replacement or fabricated data is used.

| Workbook | Rows | Columns | Notable fields |
|---|---:|---:|---|
| Labelled | 54,391 raw | 10 | `job_title`, `location`, `industry`, `salary_range`, `company_profile`, `job_desc`, `skills_desc`, `employment_type`, `fraudulent`, `text` |
| Unlabelled | 126,549 | 9 | `title`, `location`, `salary_range`, `company_profile`, `job_desc`, `skills_desc`, `employment_type`, `No of reviews`, `text_input` |

The labelled workbook contains 3,238 exact duplicate rows. The `fraudulent` target has 31,522 legitimate labels, 12,523 fraudulent labels, and 10,346 missing labels before cleaning. The training script excludes missing targets, removes exact duplicates, and uses a fixed stratified cap of 5,000 labelled rows for bounded reproducible local training; this cap is recorded in `artifacts/overview.json`. The resulting experiment uses an 80/20 stratified split: 4,000 training rows and 1,000 held-out test rows.

Text is lowercased, HTML and URLs are normalized, and whitespace is collapsed. Terms that may explain fraud risk—salary promises, urgency, contact patterns, payment requests, and low-barrier hiring language—are retained. TF-IDF is fitted only on the training partition with word unigrams and bigrams, sublinear term frequency, and a compact 1,000-feature vocabulary. The selected Logistic Regression model is persisted as both a Python `joblib` bundle and a portable JSON bundle for server-side inference.

Run the full pipeline with:

```bash
python3 scripts/train_model.py
```

The source workbook files are kept in the local `data/` folder for reproducibility during development. The deployed interface uses only the compact persisted artifacts in `artifacts/`, avoiding the need to ship large raw workbooks to the runtime.
