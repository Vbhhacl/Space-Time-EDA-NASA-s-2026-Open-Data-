import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from data_engine import load_and_clean_data, recalibrate_baseline, run_pca_on_seasons, calculate_volatility

# ==========================================
# 1. FRONTEND CONFIGURATION
# ==========================================
st.set_page_config(page_title="NASA Climate EDA", layout="wide", page_icon="🌍")
st.title("🌍 Space-Time EDA: Recalibrating NASA's Climate Baselines")
st.markdown("""
*An interactive exploratory data analysis of the NASA GISTEMP dataset, focusing on mathematical recalibration, principal component analysis (PCA), and time-series volatility.*
""")

# ==========================================
# 2. LOAD DATA (Cached for performance)
# ==========================================
@st.cache_data
def fetch_data():
    return load_and_clean_data('global_temps.csv')

df_raw, month_cols = fetch_data()

# ==========================================
# 3. SIDEBAR (User Inputs)
# ==========================================
st.sidebar.header("Data Engineering Parameters")

# Let the user play with the mathematical baseline!
st.sidebar.subheader("1. Recalibrate Baseline")
start_yr, end_yr = st.sidebar.slider(
    "Select Pre-Industrial Baseline Years:",
    min_value=1880, max_value=2023, value=(1880, 1900)
)

# Let the user set the rolling window for statistics
st.sidebar.subheader("2. Statistical Volatility")
roll_window = st.sidebar.slider("Rolling Window (Years):", min_value=5, max_value=30, value=10)

# ==========================================
# 4. RUN BACKEND ALGORITHMS
# ==========================================
# Recalibrate
df_recalibrated = recalibrate_baseline(df_raw, month_cols, start_yr, end_yr)

# Calculate Volatility
df_volatility = calculate_volatility(df_recalibrated, window=roll_window)

# Run PCA
df_pca, variance = run_pca_on_seasons(df_recalibrated, month_cols)


# ==========================================
# 5. FRONTEND VISUALIZATIONS
# ==========================================

tab1, tab2, tab3 = st.tabs(["🔥 The Heatmap", "📈 Volatility Analysis", "🧬 PCA Seasonal Shifts"])

# --- TAB 1: HEATMAP ---
with tab1:
    st.subheader(f"Global Temperature Anomalies (Baseline: {start_yr}-{end_yr})")
    st.write("This matrix shows how every single month compares to your chosen historical baseline.")
    
    # Melt data for Plotly Heatmap
    df_melt = df_recalibrated.melt(id_vars=['Year'], value_vars=month_cols, var_name='Month', value_name='Anomaly')
    
    fig_heat = px.density_heatmap(
        df_melt, x="Month", y="Year", z="Anomaly", 
        histfunc="avg", color_continuous_scale="RdBu_r",
        range_color=[-2, 2] # Lock scale to make the color shift dramatic
    )
    fig_heat.update_layout(height=600)
    st.plotly_chart(fig_heat, use_container_width=True)

# --- TAB 2: VOLATILITY ---
with tab2:
    st.subheader(f"Climate Volatility ({roll_window}-Year Rolling Standard Deviation)")
    st.write("Does a warming planet also mean a more chaotic, mathematically unpredictable planet? This chart tracks the standard deviation of temperatures over time.")
    
    fig_vol = px.line(df_volatility, x='Year', y='Annual_Volatility', markers=True)
    fig_vol.update_traces(line_color='#FF4B4B')
    fig_vol.update_layout(yaxis_title="Standard Deviation (°C)", height=500)
    st.plotly_chart(fig_vol, use_container_width=True)

# --- TAB 3: DIMENSIONALITY REDUCTION (PCA) ---
with tab3:
    st.subheader("Principal Component Analysis: Tracking Seasonal Signatures")
    st.write(f"**Component 1 (X-Axis):** Captures {variance[0]*100:.1f}% of the variance (The overall warming trend).")
    st.write(f"**Component 2 (Y-Axis):** Captures {variance[1]*100:.1f}% of the variance (Seasonal extremity and volatility).")
    
    fig_pca = px.scatter(
        df_pca, x='PCA_1 (Overall Trend)', y='PCA_2 (Seasonal Volatility)',
        color='Year', color_continuous_scale='Turbo', hover_data=['Year']
    )
    fig_pca.update_layout(height=600)
    st.plotly_chart(fig_pca, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("👨‍💻 **Developed for Data Science Portfolio** | Uses pure mathematical EDA & dimensionality reduction to extract insights from raw spatial-temporal data.")