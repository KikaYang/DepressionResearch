import pandas as pd
from pathlib import Path
import kagglehub

# ---------- Tools that we used ----------

def yesno_to01(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return pd.to_numeric(s, errors="coerce").astype("Int64")
    x = s.astype(str).str.strip().str.lower()
    return x.map({"yes": 1, "no": 0, "1": 1, "0": 0, "true": 1, "false": 0}).astype("Int64")

def age_group(age: pd.Series) -> pd.Series:
    age = pd.to_numeric(age, errors="coerce")
    bins = [0, 17, 24, 34, 44, 54, 64, 200]
    labels = ["<=17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
    return pd.cut(age, bins=bins, labels=labels, include_lowest=True)

def diet_group(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.lower()
    x = x.replace({"healthy": "Healthy", "moderate": "Moderate", "unhealthy": "Unhealthy"})
    x = x.where(x.isin(["Healthy", "Moderate", "Unhealthy"]))
    return x

def sleep_bucket_from_duration(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.replace("'", "", regex=False).str.strip().str.lower()
    def bucket(v: str):
        if "less than 5" in v:
            return "Short"
        if "5-6" in v or "5 - 6" in v:
            return "Short"
        if "7-8" in v or "7 - 8" in v:
            return "Normal"
        if "more than 8" in v:
            return "Long"
        return pd.NA
    return x.map(bucket)

def fin_bucket_from_stress(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    out = pd.Series(pd.NA, index=x.index, dtype="object")
    out[(x >= 1) & (x <= 2)] = "Low"
    out[x == 3] = "Medium"
    out[(x >= 4) & (x <= 5)] = "High"
    return out

def fin_bucket_from_income(income: pd.Series) -> pd.Series:
    x = pd.to_numeric(income, errors="coerce")
    q1 = x.quantile(1/3)
    q2 = x.quantile(2/3)
    out = pd.Series(pd.NA, index=x.index, dtype="object")
    out[x <= q1] = "Low"
    out[(x > q1) & (x <= q2)] = "Medium"
    out[x > q2] = "High"
    return out

def summarize_rate(df: pd.DataFrame, outcome_col: str, group_cols: list[str]) -> pd.DataFrame:
    d = df[group_cols + [outcome_col, "source_dataset"]].copy()
    d = d.dropna(subset=group_cols)
    g = d.groupby(group_cols + ["source_dataset"], dropna=False)
    out = g[outcome_col].agg(
        n="size",
        rate=lambda x: float(x.mean()) if x.notna().any() else None
    ).reset_index()
    out["metric"] = outcome_col
    return out

def pick_csv(folder: Path, keyword: str | None = None) -> Path:
    csvs = sorted(folder.rglob("*.csv"))
    if not csvs:
        raise FileNotFoundError(f"No CSV found under {folder}")
    if keyword:
        for p in csvs:
            if keyword.lower() in p.name.lower():
                return p
    # pick the largest csv file
    return max(csvs, key=lambda p: p.stat().st_size)

# ---------- read three datasets：using the real column name ----------

def load_student(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # if the column name doesn't match it will be KeyError
    df = df[[
        "Age",
        "Dietary Habits",
        "Sleep Duration",
        "Financial Stress",
        "Family History of Mental Illness",
        "Depression",
    ]].copy()

    df["age_group"] = age_group(df["Age"])
    df["diet_group"] = diet_group(df["Dietary Habits"])
    df["sleep_bucket"] = sleep_bucket_from_duration(df["Sleep Duration"])
    df["financial_bucket"] = fin_bucket_from_stress(df["Financial Stress"])
    df["family_history_flag"] = yesno_to01(df["Family History of Mental Illness"])
    df["depression_flag"] = yesno_to01(df["Depression"])

    df["source_dataset"] = "student"
    return df

def load_professional(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df = df[[
        "Age",
        "Dietary Habits",
        "Sleep Duration",
        "Financial Stress",
        "Family History of Mental Illness",
        "Depression",
        "Have you ever had suicidal thoughts ?",
    ]].copy()

    df["age_group"] = age_group(df["Age"])
    df["diet_group"] = diet_group(df["Dietary Habits"])
    df["sleep_bucket"] = sleep_bucket_from_duration(df["Sleep Duration"])
    df["financial_bucket"] = fin_bucket_from_stress(df["Financial Stress"])
    df["family_history_flag"] = yesno_to01(df["Family History of Mental Illness"])
    df["depression_flag"] = yesno_to01(df["Depression"])
    df["suicidal_flag"] = yesno_to01(df["Have you ever had suicidal thoughts ?"])

    df["source_dataset"] = "professional"
    return df

def load_general_proxy(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    df = df[[
        "Age",
        "Dietary Habits",
        "Income",
        "Family History of Depression",
        "History of Mental Illness",
    ]].copy()

    df["age_group"] = age_group(df["Age"])
    df["diet_group"] = diet_group(df["Dietary Habits"])
    df["financial_bucket"] = fin_bucket_from_income(df["Income"])
    df["family_history_flag"] = yesno_to01(df["Family History of Depression"])

    # proxy outcome（not same as depression）
    df["proxy_flag"] = yesno_to01(df["History of Mental Illness"])

    df["source_dataset"] = "general_proxy"
    return df

# ---------- main work flow：download -> find csv -> clean -> agg -> mash-up ----------

def main():
    prof_dir = Path(kagglehub.dataset_download("ikynahidwin/depression-professional-dataset"))
    student_dir = Path(kagglehub.dataset_download("adilshamim8/student-depression-dataset"))
    general_dir = Path(kagglehub.dataset_download("anthonytherrien/depression-dataset"))

    prof_csv = pick_csv(prof_dir, keyword="professional")
    student_csv = pick_csv(student_dir, keyword="student")
    general_csv = pick_csv(general_dir, keyword="depression")

    print("Using CSV files:")
    print(" - professional:", prof_csv)
    print(" - student     :", student_csv)
    print(" - general     :", general_csv)

    student = load_student(student_csv)
    prof = load_professional(prof_csv)
    general = load_general_proxy(general_csv)

    group_cols = ["age_group", "diet_group", "financial_bucket", "family_history_flag"]

    s_sum = summarize_rate(student, "depression_flag", group_cols)
    p_sum = summarize_rate(prof, "depression_flag", group_cols)
    g_sum = summarize_rate(general, "proxy_flag", group_cols)

    mash = pd.concat([s_sum, p_sum, g_sum], ignore_index=True)

    outdir = Path("data/processed")
    outdir.mkdir(parents=True, exist_ok=True)
    outpath = outdir / "mashup_summary.csv"
    mash.to_csv(outpath, index=False)

    print(f"OK -> {outpath}")

if __name__ == "__main__":
    main()
