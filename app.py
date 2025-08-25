
import os
import pandas as pd
import numpy as np
import streamlit as st

from src.data_prep import load_any, clean_dataframe
from src.forecasting import forecast_all
from src.correlation import correlation_matrix, propagate_change
from src.visualization import line_timeseries, heatmap_corr

st.set_page_config(page_title="KPI Predictor Dashboard", layout="wide")
st.title("📈 KPI Predictor Dashboard For Car Dealership")

with st.sidebar:
    st.header("Data Source")
    uploaded = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx"])
    use_default = st.checkbox("Use included demo file", value=True)
    st.caption("Columns required: account_id, english_name, dealer_code, year, month, monthly_value, yearly_value")
    periods = st.number_input("Forecast horizon (months)", min_value=1, max_value=12, value=3, step=1)

@st.cache_data(show_spinner=False)
def load_data(uploaded, use_default: bool):
    if uploaded is not None:
        tmp = "uploaded.tmp"
        with open(tmp, "wb") as f:
            f.write(uploaded.getbuffer())
        df = load_any(tmp)
        os.remove(tmp)
        return clean_dataframe(df)
    if use_default:
        return clean_dataframe(load_any("data/FS-data-80475.csv"))
    return None

df = load_data(uploaded, use_default)

if df is None or df.empty:
    st.warning("Please provide a dataset to continue.")
    st.stop()

# persist cleaned
os.makedirs("outputs", exist_ok=True)
df.to_csv("outputs/cleaned.csv", index=False)

tab_overview, tab_forecast, tab_corr, tab_whatif = st.tabs(["Overview","Forecast","Correlation","What‑If"])

with tab_overview:
    st.subheader("Cleaned Dataset")
    st.dataframe(df.head(100))
    st.caption(f"Rows: {len(df):,} | KPIs: {df['english_name'].nunique()} | Dates: {df['date'].min().date()} → {df['date'].max().date()}")

    agg = df.groupby(["date","english_name"], as_index=False)["monthly_value"].mean()
    st.plotly_chart(line_timeseries(agg, "date", "monthly_value", "english_name", "Historical Monthly Values"), use_container_width=True)

with tab_forecast:
    st.subheader(f"Forecast: Next {periods} Month(s)")
    with st.spinner("Training lightweight PROPHET models..."):
        forecasts = forecast_all(df, periods=int(periods))

    # Join last 12m of history for the selected KPI
    kpis = sorted(df["english_name"].unique().tolist())
    kpi = st.selectbox("Select KPI to visualize", kpis, index=0 if kpis else None, key="kpi_forecast")
    if kpi:
        hist = df[df["english_name"]==kpi].sort_values("date").tail(24).copy()
        hist["type"] = "Actual"
        f_kpi = forecasts[forecasts["english_name"]==kpi].copy()
        f_kpi["type"] = "Forecast"
        f_kpi = f_kpi.rename(columns={"predicted_monthly_value":"monthly_value"})
        combo = pd.concat([hist[["date","monthly_value","english_name","type"]], f_kpi[["date","monthly_value","english_name","type"]]])
        st.plotly_chart(line_timeseries(combo, "date", "monthly_value", "type", f"{kpi}: Actual vs Forecast"), use_container_width=True)

    st.download_button("🔽 Download all forecasts (CSV)", forecasts.to_csv(index=False).encode("utf-8"), "forecast_3m.csv", "text/csv")

    # Save for other tabs
    st.session_state["forecasts"] = forecasts

with tab_corr:
    st.subheader("KPI Correlation Matrix")
    corr = correlation_matrix(df)
    st.plotly_chart(heatmap_corr(corr), use_container_width=True)
    st.download_button("🔽 Download correlation (CSV)", corr.to_csv().encode("utf-8"), "correlation.csv", "text/csv")
    st.session_state["corr"] = corr

with tab_whatif:
    st.subheader("What‑If: Propagate KPI Change")
    forecasts = st.session_state.get("forecasts")
    corr = st.session_state.get("corr")
    if forecasts is None or corr is None:
        st.info("Run Forecast and Correlation tabs first to populate data.")
    else:
        kpis = sorted(forecasts["english_name"].unique().tolist())
        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_sel = st.selectbox("Target KPI", kpis, index=0 if kpis else None, key="kpi_whatif")
        with col2:
            pct = st.slider("Percent change to target KPI (applies to a single month)", -50, 50, value=10, step=1)
        with col3:
            months = sorted(forecasts["date"].unique())
            month_sel = st.selectbox("Month", [pd.to_datetime(m) for m in months], format_func=lambda d: d.strftime("%b %Y")) if months else None

        if kpi_sel and month_sel is not None:
            updated = propagate_change(corr, forecasts, kpi_sel, pct, month_sel)
            base_pivot = forecasts.pivot_table(index="date", columns="english_name", values="predicted_monthly_value").reset_index()
            upd_pivot = updated.pivot_table(index="date", columns="english_name", values="predicted_monthly_value").reset_index()

            st.plotly_chart(line_timeseries(base_pivot.melt(id_vars="date", var_name="english_name", value_name="predicted_monthly_value"),
                                            "date","predicted_monthly_value","english_name","Baseline Forecasts"),
                                            use_container_width=True)
            st.plotly_chart(line_timeseries(upd_pivot.melt(id_vars="date", var_name="english_name", value_name="predicted_monthly_value"),
                                            "date","predicted_monthly_value","english_name","After What‑If"),
                                            use_container_width=True)

            st.dataframe(updated.sort_values(["english_name","date"]).reset_index(drop=True))
            st.download_button("🔽 Download What‑If results (CSV)", updated.to_csv(index=False).encode("utf-8"), "whatif_results.csv", "text/csv")
