# Depression Research

## The Aim of The Project

The aim of this project is to investigate whether financial hardship is consistently associated with elevated mental health risk signals across heterogeneous open datasets. We integrate (mash-up) three Kaggle datasets representing students, professionals, and a broader population by harmonizing key variables (e.g., age group, dietary habits, family history, and a unified financial-hardship axis derived from financial stress or income). Because depression labels are not available in the general dataset, we use “history of mental illness” as a proxy indicator and compare trend directions rather than absolute prevalence across sources. The project emphasizes reproducibility, responsible data reuse, and transparent documentation of provenance, licensing, and ethical considerations, and it publishes processed outputs and visualizations via a one-page website with machine-readable metadata (DCAT-AP).

## Technical analysis

1. Data sources & acquisition
This project uses three public Kaggle CSV datasets representing students, professionals, and a broader population sample. Data are downloaded and read via scripts (e.g., using `kagglehub`) while keeping the raw files unchanged to ensure reproducibility. Because datasets differ in sampling frames and schemas, explicit mapping and harmonisation are required before comparison.

2. Why we do not perform a row-level join
The three datasets are not collected from the same individuals and do not share a common unique identifier. Therefore, a row-level join would create artificial, invalid person-to-person matches. Instead, we apply a **group-level mash-up**: we compute comparable group statistics within each dataset and then combine the aggregated results for comparison.

3. Schema mapping & harmonisation
Field names and representations vary across datasets. We harmonise them into a shared schema, including:
- `Age` → `age_group` (binned categories)
- `Dietary Habits` → `diet_group` (Healthy/Moderate/Unhealthy)
- Family mental health history → `family_history_flag` (Yes/No → 1/0)
- Outcome variables:
  - student/professional: `depression_flag` (Depression Yes/No → 1/0)
  - general: no depression label; we use `proxy_flag` (History of Mental Illness → 1/0) as a proxy risk signal

4. Cleaning & preprocessing
We perform preprocessing to improve computability and reduce noise:  
- **Boolean normalisation**: Yes/No and similar values mapped to 1/0.  
- **Category normalisation**: unify spelling/casing.  
- **Binning**: convert continuous values into interpretable buckets:
  - `age` → `age_group`
  - financial stress (1–5) → Low/Medium/High (student/professional)
  - income → terciles Low/Medium/High (general)
- **Missingness & small groups**: drop records with missing key dimensions and apply a minimum group size threshold (e.g., `MIN_N=30`) to reduce unstable estimates and potential misinterpretation.

5. Aligning “financial” into a unified hardship axis
A key technical challenge is that “High” does not mean the same thing across datasets:
- student/professional: High = **high financial stress** → worse conditions
- general: High = **high income** → better conditions
To avoid semantic mismatch, we define a unified `hardship_bucket` (Low=better, High=worse):
- student/professional: `hardship_bucket` = stress_bucket
- general: invert income buckets (low income → high hardship, high income → low hardship)

6. Group-level mash-up: computing group rates
Within each dataset, we compute group statistics using shared grouping keys (e.g., `age_group + diet_group + hardship_bucket + family_history_flag`):
- `n`: group sample size
- `rate`: risk prevalence (mean of a 0/1 flag)
This produces `mashup_summary.csv`, and a publication-ready version `mashup_summary_public.csv` after filtering small/invalid groups.

7. Trend consistency check
Because the general dataset uses a proxy outcome, we do not compare absolute prevalence across sources. Instead, we compare **directional trends** along the hardship axis (Low→Medium→High) and stratify by `family_history_flag` (0/1). We output trend plots to assess cross-source robustness.

8. Reproducible outputs & publication
We publish processed aggregates and visualisations:
- `mashup_summary_public.csv` (publishable aggregate)
- hardship trend plots (stratified by family history)
