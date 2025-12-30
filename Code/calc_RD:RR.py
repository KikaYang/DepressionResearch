import pandas as pd

m = pd.read_csv("mashup_summary_public.csv")

# select the real derpession rate（student/professional）
d = m[m["metric_readable"] == "depression_rate"].copy()
d = d[d["source_dataset"].isin(["student", "professional"])]

group_keys = ["age_group", "diet_group", "family_history_flag", "source_dataset"]

# make financial_bucket as column（Low/Medium/High），rate as value
pivot = d.pivot_table(
    index=group_keys,
    columns="financial_bucket",
    values="rate",
    aggfunc="first"
).reset_index()

# calculate the RD & RR
pivot["RD_high_low"] = pivot["High"] - pivot["Low"]
pivot["RR_high_low"] = pivot["High"] / pivot["Low"]

# if Low=0 then output inf/NaN
pivot = pivot.replace([float("inf"), -float("inf")], pd.NA)

pivot.to_csv("effect_size_by_group.csv", index=False)
print("Saved -> effect_size_by_group.csv", pivot.shape)
