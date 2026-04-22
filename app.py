import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from data_engine import load_and_clean_data, recalibrate_baseline, calculate_volatility, generate_prediction

# ==========================================
# 1. FRONTEND CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="TerraPulse Analytics", layout="wide", page_icon="🌍")

# The Deep Space Navy Theme
st.markdown("""
    <style>
    .stApp { background-color: #0B132B; }
    [data-testid="stSidebar"] { background-color: #1C2541; }
    h1, h2, h3, p, span, div, label { color: #E2E8F0 !important; }
    hr { border-color: #3A506B !important; }
    [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOAD & PROCESS DATA
# ==========================================
@st.cache_data
def fetch_data():
    return load_and_clean_data('global_temps.csv')

df_raw, month_cols = fetch_data()

# ==========================================
# 3. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=100)
    st.markdown("### ⚙️ System Parameters")
    
    start_yr, end_yr = st.slider("Select Pre-Industrial Baseline:", 1880, 2023, (1880, 1900))
    st.caption("Recalculates all historical temperatures relative to this era.")
    st.markdown("---")
    st.markdown("📊 **Data Source:** NASA GISTEMP v4")

df_recal = recalibrate_baseline(df_raw, month_cols, start_yr, end_yr)
df_annual = df_recal[['Year', 'J-D']].dropna()

latest_year = int(df_annual['Year'].max())
latest_temp = df_annual[df_annual['Year'] == latest_year]['J-D'].values[0]
hottest_year = int(df_annual.loc[df_annual['J-D'].idxmax()]['Year'])
hottest_temp = df_annual['J-D'].max()

# ==========================================
# 4. HEADER & KPI CARDS
# ==========================================
st.title("🌍 TerraPulse Analytics")
st.markdown("Tracking historical temperature anomalies and projecting future climate scenarios based on NASA Goddard Institute data.")
st.divider() 

col1, col2, col3 = st.columns(3)
col1.metric(f"Current Warming (As of {latest_year})", f"+{latest_temp:.2f} °C", "Critical Threshold: 1.5 °C", delta_color="inverse")
col2.metric("Hottest Year on Record", str(hottest_year), f"+{hottest_temp:.2f} °C above baseline", delta_color="inverse")
col3.metric("Historical Baseline Used", f"{start_yr} - {end_yr}", "Active")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. TABBED NAVIGATION
# ==========================================
tab1, tab2, tab3 = st.tabs(["📊 Executive Summary", "🔬 Data Deep Dive", "🔮 Future Projections"])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    st.subheader("The Macro Trend: Historical Trajectory")
    
    fig_area = px.area(df_annual, x='Year', y='J-D', color_discrete_sequence=['#FF4B4B'])
    fig_area.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text=f"Baseline ({start_yr}-{end_yr})")
    fig_area.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, l=0, r=0, b=0), yaxis_title="Anomaly (°C)")
    fig_area.update_xaxes(showgrid=True, gridcolor='#1C2541')
    fig_area.update_yaxes(showgrid=True, gridcolor='#1C2541')
    
    st.plotly_chart(fig_area, use_container_width=True)
    
    with st.expander("📖 What does this graph mean?"):
        st.write("This graph plots the annual global temperature anomaly against the selected pre-industrial baseline over time. By utilizing an area chart, the cumulative volume of the anomaly becomes visually apparent. It serves as the primary indicator of global warming, showing a distinct upward trajectory from the mid-20th century onwards. The reference dashed line at 0.0 °C clearly illustrates how modern temperatures consistently overshoot the historical norm.")

    st.markdown("---")
    st.subheader("The Warming Stripes")
    fig_stripes = px.imshow([df_annual['J-D'].values], color_continuous_scale="RdBu_r", zmin=-1.5, zmax=1.5, aspect="auto")
    fig_stripes.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showticklabels=False, showgrid=False), margin=dict(l=0, r=0, t=10, b=30), height=150, coloraxis_showscale=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_stripes, use_container_width=True)
    
    with st.expander("📖 What does this graph mean?"):
        st.write("Inspired by climate scientist Ed Hawkins, this visualization strips away numerical axes to present a purely chronological sequence of colored stripes. Each stripe represents a single year, colored from dark blue (cooler than average) to dark red (warmer than average). This is a powerful, minimalist tool for communicating the stark reality of climate shifts, condensing massive amounts of temporal data into an immediately recognizable pattern of escalating global heat.")

# --- TAB 2: DATA DEEP DIVE ---
with tab2:
    st.subheader("Seasonal Heatmap Matrix")
    df_melt = df_recal.melt(id_vars=['Year'], value_vars=month_cols, var_name='Month', value_name='Anomaly')
    fig_heat = px.density_heatmap(df_melt, x="Month", y="Year", z="Anomaly", histfunc="avg", color_continuous_scale="RdBu_r", range_color=[-1.5, 1.5])
    fig_heat.update_layout(height=500, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_heat, use_container_width=True)
    
    with st.expander("📖 What does this graph mean?"):
        st.write("This 2D matrix plots 'Months' on the X-axis and 'Years' on the Y-axis, using a diverging color scale (Blue to Red) to represent the temperature anomaly for that specific time intersection. While the Area Chart shows annual averages, the Heatmap reveals *seasonal* volatility. It allows users to observe whether winters are warming faster than summers, or if specific months exhibit abnormal temperature spikes across decades.")

    st.markdown("---")
    st.subheader("Mathematical Volatility (10-Year Rolling Std Dev)")
    df_volatility = calculate_volatility(df_recal, window=10)
    fig_vol = px.line(df_volatility.dropna(), x='Year', y='Annual_Volatility', markers=True)
    fig_vol.update_traces(line_color='#FFA500')
    fig_vol.update_layout(yaxis_title="Standard Deviation (°C)", height=400, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    fig_vol.update_xaxes(showgrid=True, gridcolor='#1C2541')
    fig_vol.update_yaxes(showgrid=True, gridcolor='#1C2541')
    st.plotly_chart(fig_vol, use_container_width=True)
    
    with st.expander("📖 What does this graph mean?"):
        st.write("This line chart does not plot temperatures; instead, it plots the *Standard Deviation* of temperatures over a rolling 10-year window. This graph acts as a proxy for climate instability. A rising standard deviation indicates that global temperatures are not just rising, but becoming increasingly erratic and unpredictable, which is a critical metric for understanding extreme weather patterns.")

# --- TAB 3: FUTURE PROJECTIONS ---
with tab3:
    st.subheader("Machine Learning Trajectory Forecast")
    
    target_year = st.slider("Select a Future Target Year:", min_value=2025, max_value=2100, value=2050, step=1)
    
    prediction, trend_df = generate_prediction(df_recal, target_year)
    
    st.metric(f"Projected Anomaly in {target_year}", f"+{prediction:.2f} °C", delta="Estimated", delta_color="off")
    
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Scatter(x=df_annual['Year'], y=df_annual['J-D'], mode='lines', name='Historical Data', line=dict(color='#82a0d8', width=2)))
    fig_pred.add_trace(go.Scatter(x=trend_df['Year'], y=trend_df['Predicted_Anomaly'], mode='lines', name='ML Projection', line=dict(color='#FF4B4B', width=3, dash='dash')))
    fig_pred.add_trace(go.Scatter(x=[target_year], y=[prediction], mode='markers', name=f'{target_year} Estimate', marker=dict(color='#FFEB3B', size=12, symbol='star')))
    
    fig_pred.add_hline(y=0, line_dash="solid", line_color="gray", annotation_text="Baseline")
    fig_pred.add_hline(y=1.5, line_dash="dot", line_color="#F59E0B", annotation_text="1.5°C Threshold")
    
    fig_pred.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Anomaly (°C)", xaxis_title="Year",
        hovermode="x unified", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    fig_pred.update_xaxes(showgrid=True, gridcolor='#1C2541')
    fig_pred.update_yaxes(showgrid=True, gridcolor='#1C2541')
    
    st.plotly_chart(fig_pred, use_container_width=True)
    
    with st.expander("📖 What does this graph mean?"):
        st.write("This visualization overlays an interactive, 2nd-degree Polynomial Regression trendline on top of the historical data points. It extends along the X-axis into future dates based on user input. It transforms the dashboard from a purely historical EDA tool into a predictive analytics platform. By mathematically capturing the non-linear acceleration of global warming, it provides stakeholders with a visual estimation of when we might cross critical climate thresholds (such as the 1.5°C mark).")

# ==========================================
# 6. PROFESSIONAL REFERENCES
# ==========================================
st.divider()
st.caption("""
**References & Methodology:**
* Data sourced from the NASA Goddard Institute for Space Studies (GISS).
* Modeling uses Scikit-Learn Polynomial Regression (Degree=2) to capture nonlinear acceleration. Projections are mathematical trend extrapolations, not complex climatological simulations.
""")