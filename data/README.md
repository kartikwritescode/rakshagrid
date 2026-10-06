# Raksha Grid Data Repository

This directory contains datasets supporting model training, evaluation, and geospatial analytics.

## Directory Structure

```text
data/
├── raw/
│   ├── sources/                  # Raw incident reports and scraped call transcripts
│   ├── train.csv                 # Supervised scam training set
│   ├── val.csv                   # Supervised scam validation set
│   ├── test.csv                  # Supervised scam test holdout
│   ├── combined_all.csv          # Aggregate scam classification corpus
│   └── adversarial_eval.csv      # Phishing and evasion robustness benchmarks
├── processed/
│   └── points.parquet            # Geocoded cybercrime incident coordinates for DBSCAN clustering
└── synthetic_reports.json        # Test fixture of victim-phone-UPI network entities
```

## Datasets

1. **Scam Call Transcripts (`raw/*.csv`)**:
   - `train.csv`, `val.csv`, `test.csv`: Labeled conversational transcripts (legitimate, borderline, digital arrest, financial fraud).
   - `adversarial_eval.csv`: Evasion benchmarks designed to stress-test rules, TF-IDF, and Transformer models.

2. **Geospatial Incidents (`processed/points.parquet`)**:
   - Apache Parquet file containing lat/long coordinates, timestamps, and crime classifications used by `rakshagrid.ai_crime` to compute Haversine DBSCAN hotspots.
