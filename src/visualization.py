
import pandas as pd
import plotly.express as px

def line_timeseries(df: pd.DataFrame, date_col: str, value_col: str, color_col: str = None, title: str = ""):
    fig = px.line(df, x=date_col, y=value_col, color=color_col, markers=True, title=title)
    fig.update_layout(margin=dict(l=10,r=10,t=40,b=10))
    return fig

def heatmap_corr(corr: pd.DataFrame, title: str = "KPI Correlation"):
    fig = px.imshow(corr, text_auto=True, aspect="auto", title=title, color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    fig.update_layout(margin=dict(l=10,r=10,t=40,b=10))
    return fig
