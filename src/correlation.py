import pandas as pd

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    wide = df.pivot_table(index="date", columns="english_name", values="monthly_value", aggfunc="mean")
    corr = wide.corr(method="pearson").fillna(0.0)
    return corr

def propagate_change(corr: pd.DataFrame,
                     forecasts: pd.DataFrame,
                     target_kpi: str,
                     pct_change: float,
                     month) -> pd.DataFrame:
    out = forecasts.copy()
    
    # The original line caused a ValueError because the `month` variable is already a Timestamp.
    # It is not necessary to convert it again.
    
    m_mask = out["date"] == month
    t_mask = out["english_name"] == target_kpi
    out.loc[m_mask & t_mask, "predicted_monthly_value"] *= (1 + pct_change/100.0)

    if target_kpi in corr.columns:
        for other in out["english_name"].unique():
            if other == target_kpi or other not in corr.index:
                continue
            weight = corr.loc[other, target_kpi]
            o_mask = (out["english_name"] == other) & (out["date"] == month)
            out.loc[o_mask, "predicted_monthly_value"] *= (1 + weight * (pct_change/100.0))
    return out