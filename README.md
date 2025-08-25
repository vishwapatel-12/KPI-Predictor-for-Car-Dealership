
📊 KPI Predictor Dashboard:

This project is an interactive data analysis and forecasting dashboard built with Streamlit.  It allows users to upload datasets, explore correlations, visualize trends, and perform time-series forecasting using Facebook Prophet.The tool is designed to help in decision-making by providing insights from raw data in a simple and visual manner.

✨ Features:

- 🔄 Data preprocessing and cleaning
- 📈 Correlation analysis
- 📊 Interactive data visualizations with Plotly
- ⏳ Time series forecasting using Prophet
- 🖥 Streamlit dashboard for easy interaction


🗂 Project Structure:
The codebase is organized into the following modules:

- app.py: The main script that runs the Streamlit web application, tying together all the other components     into an interactive dashboard.
- data_prep.py: Contains functions for data cleaning, validation, and preparation.
- forecasting.py: Implements the Prophet model for generating time series forecasts.
- correlation.py: Provides the logic for calculating KPI correlations and     propagating changes for the "what-if" analysis.
- visualization.py: Defines the functions for creating interactive line charts and heatmaps.


⚙️ Quick Start (Windows / VS Code):
Open PowerShell/Terminal in your project folder and run the following commands step by step:
step 1:Create a virtual environment (recommended):
       python -m venv .venv

step 2 - Activate the environment:

     . .venv\Scripts\Activate

step 3:

       python -m pip install --upgrade pip

step 4 - Install dependencies:

       pip install -r requirements.txt

step 5 - Run the Streamlit app:

      streamlit run app.py

step 6 - Then open your browser and go to:

       http://localhost:8501/

📦 Dependencies:
The project uses the following Python libraries:

- numpy – Numerical operations
- pandas – Data manipulation and cleaning
- plotly – Interactive data visualizations
- prophet – Time-series forecasting
- streamlit – Web-based dashboard
- All dependencies are listed in requirements.txt

📂 Data:

Default demo file: `data/FS-data-80475.csv` with columns:
`account_id, english_name, dealer_code, year, month, monthly_value, yearly_value`
You can also upload a CSV/Excel from the sidebar.

📑 Outputs:

- `outputs/cleaned.csv` – cleaned dataset after preprocessing
- `outputs/forecast_3m.csv` – 3‑month forecasts
- `outputs/correlation.csv` – KPI correlation matrix
