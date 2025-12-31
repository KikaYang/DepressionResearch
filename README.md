# Depression Research

## The Aim of The Project

The aim of this project is to investigate whether financial hardship is consistently associated with elevated mental health risk signals across heterogeneous open datasets. We integrate (mash-up) three Kaggle datasets representing students, professionals, and a broader population by harmonizing key variables (e.g., age group, dietary habits, family history, and a unified financial-hardship axis derived from financial stress or income). Because depression labels are not available in the general dataset, we use “history of mental illness” as a proxy indicator and compare trend directions rather than absolute prevalence across sources. The project emphasizes reproducibility, responsible data reuse, and transparent documentation of provenance, licensing, and ethical considerations, and it publishes processed outputs and visualizations via a one-page website with machine-readable metadata (DCAT-AP).

## Technical analysis

1. Data sources & acquisition
This project uses three public Kaggle CSV datasets representing students, professionals, and a broader population sample. Data are downloaded and read via scripts (e.g., using `kagglehub`) while keeping the raw files unchanged to ensure reproducibility. Because datasets differ in sampling frames and schemas, explicit mapping and harmonisation are required before comparison.
