
# KPI Predictor Dashboard (Streamlit)

This project is an interactive dashboard that prepares monthly KPI data, forecasts the next 3 months for all KPIs,computes correlations, and supports an interactive What‑If simulator that propagates changes from one KPI to related KPIs.

# Features
- Data preprocessing and cleaning
- Correlation analysis
- Interactive data visualizations with Plotly
- Time series forecasting using Prophet
- Streamlit dashboard for easy interaction


## Project Structure
The codebase is organized into the following modules:

- app.py: The main script that runs the Streamlit web application, tying together all the other components     into an interactive dashboard.
- data_prep.py: Contains functions for data cleaning, validation, and preparation.
- forecasting.py: Implements the Prophet model for generating time series forecasts.
- correlation.py: Provides the logic for calculating KPI correlations and     propagating changes for the "what-if" analysis.
- visualization.py: Defines the functions for creating interactive line charts and heatmaps.


## Quick Start (Windows / VS Code)
 In powershell do following steps:
step 1: python -m venv .venv

step 2: . .venv\Scripts\Activate

step 3: python -m pip install --upgrade pip

step 4: pip install -r requirements.txt

step 5: streamlit run app.py


## Data
Default demo file: `data/FS-data-80475.csv` with columns:
`account_id, english_name, dealer_code, year, month, monthly_value, yearly_value`

You can also upload a CSV/Excel from the sidebar.

## Outputs
- `outputs/cleaned.csv` – cleaned dataset after preprocessing
- `outputs/forecast_3m.csv` – 3‑month forecasts
- `outputs/correlation.csv` – KPI correlation matrix
