import pandas as pd

m = pd.read_csv("data/processed/mashup_summary.csv")

# 1) delete the useless rows
m = m[(m["n"] > 0) & (m["rate"].notna())].copy()

# 2) set the thrshold
MIN_N = 30
m_public = m[m["n"] >= MIN_N].copy()

# 3) make metric readable
m_public["metric_readable"] = m_public["metric"].replace({
    "depression_flag": "depression_rate",
    "proxy_flag": "mental_illness_history_rate_proxy"
})

# 4) save
m_public.to_csv("mashup_summary_public.csv", index=False)
print("Saved -> mashup_summary_public.csv", m_public.shape)
