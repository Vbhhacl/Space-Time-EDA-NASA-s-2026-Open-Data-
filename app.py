import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_engine import load_and_clean_data, recalibrate_baseline, calculate_volatility

# ==========================================
# 1. FRONTEND CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="Global Climate Dashboard", layout="wide", page_icon="🌍")

# Custom CSS for a clean, Full-Stack SaaS application look
st.markdown("""
    <style>
    /* Clean up the top padding */
    .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    /* Style the KPI Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #F0F2F6;
        border: 1px solid #E0E4E8;
        padding: 5% 10% 5% 10%;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
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
# 3. SIDEBAR (Clean & Intuitive)
# ==========================================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=100)
    st.markdown("### Dashboard Controls")
    st.write("Adjust the parameters below to see how historical baselines change the data.")
    
    start_yr, end_yr = st.slider("Select Pre-Industrial Baseline:", 1880, 2023, (1880, 1900))
    st.caption("Default baseline is 1880-1900. This recalculates all temperatures relative to this era.")
    
    st.markdown("---")
    st.markdown("👨‍💻 **Developer:** [Your Name]")
    st.markdown("📊 **Data:** NASA GISTEMP v4")

# Run Backend Logic based on user inputs
df_recal = recalibrate_baseline(df_raw, month_cols, start_yr, end_yr)
df_annual = df_recal[['Year', 'J-D']].dropna()

# Calculate KPI Metrics dynamically
latest_year = int(df_annual['Year'].max())
latest_temp = df_annual[df_annual['Year'] == latest_year]['J-D'].values[0]

baseline_temp_avg = df_raw[(df_raw['Year'] >= start_yr) & (df_raw['Year'] <= end_yr)]['J-D'].mean()
total_warming = latest_temp # Because we already recalibrated, the latest temp IS the total warming
hottest_year = int(df_annual.loc[df_annual['J-D'].idxmax()]['Year'])
hottest_temp = df_annual['J-D'].max()

# ==========================================
# 4. HEADER & KPI CARDS
# ==========================================
st.title("🌍 Global Climate Acceleration Dashboard")
st.markdown("Tracking historical temperature anomalies and seasonal shifts using data from the NASA Goddard Institute for Space Studies.")

# KPI Row
col1, col2, col3 = st.columns(3)
col1.metric(label=f"Current Warming (As of {latest_year})", value=f"+{total_warming:.2f} °C", delta="Critical Threshold: 1.5 °C", delta_color="inverse")
col2.metric(label="Hottest Year on Record", value=str(hottest_year), delta=f"+{hottest_temp:.2f} °C above baseline", delta_color="inverse")
col3.metric(label="Historical Baseline Used", value=f"{start_yr} - {end_yr}", delta="Recalibrated", delta_color="normal")

st.markdown("<br>", unsafe_allow_html=True) # Spacer

# ==========================================
# 5. TABBED NAVIGATION
# ==========================================
tab1, tab2 = st.tabs(["📊 Executive Summary (Non-Tech)", "🔬 Data Deep Dive (Analysts)"])

# --- TAB 1: EXECUTIVE SUMMARY ---
with tab1:
    st.markdown("### The Macro Trend: Are we getting hotter?")
    
    # Chart 1: Clean Area Chart
    fig_area = px.area(df_annual, x='Year', y='J-D', 
                       title="Global Temperature Change Over Time",
                       labels={'J-D': 'Temperature Anomaly (°C)'},
                       color_discrete_sequence=['#FF4B4B'])
    
    # Add a zero-line to show the baseline clearly
    fig_area.add_hline(y=0, line_dash="dash", line_color="black", annotation_text=f"Baseline Average ({start_yr}-{end_yr})")
    
    fig_area.update_layout(plot_bgcolor="white", margin=dict(t=50, l=0, r=0, b=0))
    st.plotly_chart(fig_area, use_container_width=True)
    
    with st.expander("💡 How to read this chart (Click to expand)"):
        st.write("""
        * **The Black Dashed Line (0.0):** This represents the average temperature during the baseline period you selected in the sidebar.
        * **The Red Area:** Shows how much hotter (or colder) the Earth was in that specific year compared to the baseline. 
        * **The Takeaway:** Notice how the red area stays below the line until the 1940s, and then violently spikes upward after the 1980s.
        """)

    st.markdown("---")
    
    # Chart 2: Warming Stripes (Easiest chart for non-tech people to understand)
    st.markdown("### The Warming Stripes")
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
        st.write("This is a famous visualization invented by climate scientists. Every single vertical line is one year. Blue lines are years that were colder than average, and red lines are years that were hotter. It completely strips away confusing numbers so you can visually see the acceleration of global warming on the right side.")


# --- TAB 2: DATA DEEP DIVE ---
with tab2:
    st.markdown("### Seasonal Heatmap: When is the warming happening?")
    
    # Melt data for Plotly Heatmap
    df_melt = df_recal.melt(id_vars=['Year'], value_vars=month_cols, var_name='Month', value_name='Anomaly')
    
    fig_heat = px.density_heatmap(
        df_melt, x="Month", y="Year", z="Anomaly", 
        histfunc="avg", color_continuous_scale="RdBu_r",
        range_color=[-1.5, 1.5], # Lock scale to make the color shift dramatic
        title="Monthly Temperature Anomalies by Year"
    )
    fig_heat.update_layout(height=600, plot_bgcolor="white")
    st.plotly_chart(fig_heat, use_container_width=True)
    
    with st.expander("💡 Analyst Insight"):
        st.write("Unlike a standard yearly average, this matrix allows us to isolate seasonal anomalies. For example, you can look vertically down the 'Feb' column to see if winters are warming at a faster mathematical rate than summers ('Jul', 'Aug').")

    st.markdown("---")

    # Chart 4: Volatility (For the Data Scientists)
    st.markdown("### Mathematical Volatility (10-Year Rolling Standard Deviation)")
    df_volatility = calculate_volatility(df_recal, window=10)
    
    fig_vol = px.line(df_volatility.dropna(), x='Year', y='Annual_Volatility', markers=True,
                      title="Is the climate becoming more mathematically unpredictable?")
    fig_vol.update_traces(line_color='#FFA500')
    fig_vol.update_layout(yaxis_title="Standard Deviation (°C)", height=400, plot_bgcolor="white")
    
    st.plotly_chart(fig_vol, use_container_width=True)