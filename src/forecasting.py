import numpy as np
import pandas as pd
from prophet import Prophet
from .data_prep import ensure_monthly_frequency

def seasonal_naive(series: pd.Series, periods: int = 3) -> pd.Series:
    s = ensure_monthly_frequency(series).astype(float).ffill()
    if len(s) >= 12:
        last12 = s[-12:]
        reps = int(np.ceil(periods/12))
        vals = pd.concat([last12]*reps)[:periods].values
    else:
        vals = np.repeat(s.iloc[-1], periods)

    # Use "M" (month-end) then shift to month-start
    idx = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq="M")
    idx = idx + pd.offsets.MonthBegin(0)  # align to start of month
    return pd.Series(vals, index=idx)

def fit_forecast(series: pd.Series, periods: int = 3) -> pd.Series:
    s = ensure_monthly_frequency(series).astype(float).ffill()
    if s.dropna().shape[0] < 6:
        return seasonal_naive(s, periods)
    
    # Prepare data for Prophet
    df = s.reset_index()
    df.rename(columns={'index': 'ds', s.name: 'y'}, inplace=True)
    
    # Initialize and fit the Prophet model
    model = Prophet(yearly_seasonality=True, daily_seasonality=False, weekly_seasonality=False)
    model.fit(df)
    
    # Create future dataframe for forecasting
    future = model.make_future_dataframe(periods=periods, freq='MS')
    
    # Make the forecast
    forecast = model.predict(future)
    
    # Extract the forecasted values
    yhat = forecast['yhat'].iloc[-periods:]
    
    # Fix the index to month-start
    idx = pd.date_range(s.index[-1] + pd.offsets.MonthBegin(1), periods=periods, freq="M")
    idx = idx + pd.offsets.MonthBegin(0)
    
    return pd.Series(yhat.values, index=idx)

def forecast_all(df: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    out = []
    for (acc, name), g in df.groupby(["account_id", "english_name"]):
        s = g.set_index("date")["monthly_value"].sort_index()
        if s.empty:
            continue
        yhat = fit_forecast(s, periods)
        out.append(pd.DataFrame({
            "account_id": acc,
            "english_name": name,
            "date": yhat.index,
            "predicted_monthly_value": yhat.values
        }))
    if not out:
        return pd.DataFrame(columns=["account_id", "english_name", "date", "predicted_monthly_value"])
    return pd.concat(out, ignore_index=True).sort_values(["account_id", "english_name", "date"]).reset_index(drop=True)

# 🔧 Inside propagate_change (fix MS issue)
def fix_month(month):
    month = pd.to_datetime(month).to_period("M").to_timestamp()   # month-end
    month = month + pd.offsets.MonthBegin(0)                      # move to month-start
    return month