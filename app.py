import streamlit as st
import plotly.express as px
import pandas as pd
from data_engine import load_and_clean_data, recalibrate_baseline, calculate_volatility

# ==========================================
# 1. FRONTEND CONFIGURATION
# ==========================================
# Letting Streamlit handle the theme naturally!
st.set_page_config(page_title="Global Climate Dashboard", layout="wide", page_icon="🌍")

# ==========================================
# 2. LOAD & PROCESS DATA
# ==========================================
@st.cache_data
def fetch_data():
    return load_and_clean_data('global_temps.csv')

df_raw, month_cols = fetch_data()

# ==========================================
# 3. SIDEBAR (Clean & Intuitive)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=100)
    st.markdown("### Dashboard Controls")
    st.write("Adjust the parameters below to see how historical baselines change the data.")
    
    start_yr, end_yr = st.slider("Select Pre-Industrial Baseline:", 1880, 2023, (1880, 1900))
    st.caption("Default baseline is 1880-1900. This recalculates all temperatures relative to this era.")
    st.markdown("---")
    st.markdown("📊 **Data Source:** NASA GISTEMP v4")

# Run Backend Logic based on user inputs
df_recal = recalibrate_baseline(df_raw, month_cols, start_yr, end_yr)
df_annual = df_recal[['Year', 'J-D']].dropna()

# Calculate KPI Metrics dynamically
latest_year = int(df_annual['Year'].max())
latest_temp = df_annual[df_annual['Year'] == latest_year]['J-D'].values[0]
hottest_year = int(df_annual.loc[df_annual['J-D'].idxmax()]['Year'])
hottest_temp = df_annual['J-D'].max()

# ==========================================
# 4. HEADER & KPI CARDS
# ==========================================
st.title("🌍 Global Climate Acceleration Dashboard")
st.markdown("Tracking historical temperature anomalies and seasonal shifts using data from the NASA Goddard Institute for Space Studies.")
st.divider() # Native Streamlit divider

# KPI Row
col1, col2, col3 = st.columns(3)
col1.metric(label=f"Current Warming (As of {latest_year})", value=f"+{latest_temp:.2f} °C", delta="Critical Threshold: 1.5 °C", delta_color="inverse")
col2.metric(label="Hottest Year on Record", value=str(hottest_year), delta=f"+{hottest_temp:.2f} °C above baseline", delta_color="inverse")
col3.metric(label="Historical Baseline Used", value=f"{start_yr} - {end_yr}", delta="Recalibrated", delta_color="normal")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. TABBED NAVIGATION
# ==========================================
tab1, tab2 = st.tabs(["📊 Executive Summary", "🔬 Data Deep Dive"])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    st.subheader("The Macro Trend: Are we getting hotter?")
    
    # Chart 1: Clean Area Chart
    fig_area = px.area(df_annual, x='Year', y='J-D', 
                       labels={'J-D': 'Temperature Anomaly (°C)'},
                       color_discrete_sequence=['#FF4B4B'])
    
    # Add a zero-line to show the baseline clearly
    fig_area.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text=f"Baseline Average ({start_yr}-{end_yr})")
    fig_area.update_layout(margin=dict(t=30, l=0, r=0, b=0))
    st.plotly_chart(fig_area, use_container_width=True)
    
    with st.expander("💡 How to read this chart"):
        st.write("""
        * **The Dashed Line (0.0):** Represents the average temperature during the baseline period.
        * **The Red Area:** Shows how much hotter (or colder) the Earth was in that specific year compared to the baseline. 
        * **The Takeaway:** Notice the aggressive upward spike starting in the late 20th century.
        """)

    st.markdown("---")
    
    # Chart 2: Warming Stripes
    st.subheader("The Warming Stripes")
    fig_stripes = px.imshow(
        [df_annual['J-D'].values], 
        color_continuous_scale="RdBu_r", zmin=-1.5, zmax=1.5, aspect="auto"
    )
    fig_stripes.update_layout(
        xaxis=dict(tickmode='array', tickvals=list(range(0, len(df_annual), 10)), ticktext=df_annual['Year'].iloc[::10].tolist(), showgrid=False),
        yaxis=dict(showticklabels=False, showgrid=False),
        margin=dict(l=0, r=0, t=10, b=30), height=200, coloraxis_showscale=False
    )
    st.plotly_chart(fig_stripes, use_container_width=True)
    
    with st.expander("💡 What is this barcode?"):
        st.write("Every single vertical line is one year. Blue lines are colder years, and red lines are hotter years. It visually strips away numbers to show the sheer acceleration of warming on the right side.")

# --- TAB 2: DATA DEEP DIVE ---
with tab2:
    st.subheader("Seasonal Heatmap: When is the warming happening?")
    
    df_melt = df_recal.melt(id_vars=['Year'], value_vars=month_cols, var_name='Month', value_name='Anomaly')
    fig_heat = px.density_heatmap(
        df_melt, x="Month", y="Year", z="Anomaly", 
        histfunc="avg", color_continuous_scale="RdBu_r",
        range_color=[-1.5, 1.5]
    )
    fig_heat.update_layout(height=600)
    st.plotly_chart(fig_heat, use_container_width=True)
    
    with st.expander("💡 Analyst Insight"):
        st.write("This matrix allows us to isolate seasonal anomalies. Look vertically down columns like 'Feb' to compare winter warming rates versus summer months.")

    st.markdown("---")

    st.subheader("Mathematical Volatility (10-Year Rolling Std Dev)")
    df_volatility = calculate_volatility(df_recal, window=10)
    
    fig_vol = px.line(df_volatility.dropna(), x='Year', y='Annual_Volatility', markers=True)
    fig_vol.update_traces(line_color='#FFA500')
    fig_vol.update_layout(yaxis_title="Standard Deviation (°C)", height=400)
    st.plotly_chart(fig_vol, use_container_width=True)

# ==========================================
# 6. PROFESSIONAL REFERENCES
# ==========================================
st.divider()
st.caption("""
**References & Methodology:**
* Data sourced from the NASA Goddard Institute for Space Studies (GISS) Surface Temperature Analysis (GISTEMP v4).
* Lenssen, N., G. Schmidt, J. Hansen, et al., 2019: [Improvements in the GISTEMP Uncertainty Model](https://pubs.giss.nasa.gov/abs/le05800h.html). *J. Geophys. Res. Atmos.*, 124, no. 12, 6307-6326.
* GISTEMP Team, 2024: GISS Surface Temperature Analysis (GISTEMP), version 4. NASA Goddard Institute for Space Studies. Dataset accessed via [data.giss.nasa.gov/gistemp/](https://data.giss.nasa.gov/gistemp/).
""")