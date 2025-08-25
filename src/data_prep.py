
import pandas as pd

REQUIRED = [
    "account_id", "english_name", "dealer_code",
    "year", "month", "monthly_value", "yearly_value"
]

def load_any(path: str) -> pd.DataFrame:
    if path.lower().endswith(".csv"):
        return pd.read_csv(path)
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    raise ValueError("Unsupported file type (use csv/xlsx).")

def ensure_monthly_frequency(series):
    """
    Ensure the Series has a monthly frequency with datetime index
    aligned to the first day of each month.
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("Series index must be DatetimeIndex")

    s = series.copy()
    # Convert to monthly periods → timestamp at month start
    s.index = pd.to_datetime(s.index).to_period("M").to_timestamp(how="S")
    s = s.sort_index()
    # Fill missing months in between
    full_idx = pd.date_range(s.index.min(), s.index.max(), freq="MS")
    return s.reindex(full_idx)

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Validate columns
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out_frames = []
    df = df.copy()
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))

    for (acc, name), g in df.groupby(["account_id", "english_name"], as_index=False):
        s = g.set_index("date")["monthly_value"].astype(float).sort_index()
        s_full = ensure_monthly_frequency(s)
        g_full = s_full.to_frame("monthly_value").reset_index().rename(columns={"index":"date"})
        g_full["account_id"] = acc
        g_full["english_name"] = name
        g_full["dealer_code"] = g["dealer_code"].ffill().bfill().iloc[0] if not g["dealer_code"].empty else None

        # derive yearly_value if missing -> rolling 12m sum
        if "yearly_value" in g and g["yearly_value"].notna().any():
            yv = g.set_index("date")["yearly_value"].sort_index().reindex(g_full["date"]).ffill()
        else:
            yv = g_full.set_index("date")["monthly_value"].rolling(12, min_periods=1).sum()
        g_full["yearly_value"] = yv.values
        out_frames.append(g_full)

    clean = pd.concat(out_frames, ignore_index=True).sort_values(["account_id","english_name","date"]).reset_index(drop=True)
    return clean
