import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_engine import load_and_clean_data, recalibrate_baseline, run_pca_on_seasons, calculate_volatility

# ==========================================
# 1. FRONTEND CONFIGURATION
# ==========================================
st.set_page_config(page_title="NASA Climate EDA", layout="wide", page_icon="🌍")

# Custom CSS to make it look like a sleek, modern dashboard
st.markdown("""
    <style>
    .main {background-color: #0E1117;}
    h1, h2, h3 {color: #E0E0E0;}
    </style>
    """, unsafe_allow_html=True)

st.title("🌍 Space-Time EDA: Climate Acceleration")
st.markdown("*Advanced Exploratory Data Analysis mapping global temperature anomalies, volatility signatures, and multi-dimensional climate shifts.*")

# ==========================================
# 2. LOAD DATA
# ==========================================
@st.cache_data
def fetch_data():
    return load_and_clean_data('global_temps.csv')

df_raw, month_cols = fetch_data()

# ==========================================
# 3. SIDEBAR CONTROLS
# ==========================================
st.sidebar.header("⚙️ Engineering Parameters")
start_yr, end_yr = st.sidebar.slider("Pre-Industrial Baseline:", 1880, 2023, (1880, 1900))
roll_window = st.sidebar.slider("Volatility Window (Years):", 5, 30, 10)

# Run Backend Algorithms
df_recal = recalibrate_baseline(df_raw, month_cols, start_yr, end_yr)
df_pca, variance = run_pca_on_seasons(df_recal, month_cols)
df_melt = df_recal.melt(id_vars=['Year'], value_vars=month_cols, var_name='Month', value_name='Anomaly')

# ==========================================
# 4. ADVANCED VISUALIZATIONS
# ==========================================

# --- TOP SECTION: THE WARMING STRIPES ---
st.markdown("### 🌡️ The Global Warming Stripes")
st.markdown("Inspired by climatologist Ed Hawkins, this 'barcode' strips away numbers to show the sheer density of chronological temperature change. Every bar is a year.")

# Create the Stripes (Heatmap with 1 row)
df_annual = df_recal[['Year', 'J-D']].dropna()
fig_stripes = px.imshow(
    [df_annual['J-D'].values], 
    color_continuous_scale="RdBu_r", 
    zmin=-1.5, zmax=1.5,
    aspect="auto"
)
fig_stripes.update_layout(
    xaxis=dict(tickmode='array', tickvals=list(range(0, len(df_annual), 20)), ticktext=df_annual['Year'].iloc[::20].tolist(), showgrid=False),
    yaxis=dict(showticklabels=False, showgrid=False),
    margin=dict(l=0, r=0, t=10, b=30),
    height=150, coloraxis_showscale=False
)
st.plotly_chart(fig_stripes, use_container_width=True)


tab1, tab2, tab3 = st.tabs(["🌀 The Climate Spiral", "📊 Shaded Volatility Bands", "🌌 3D PCA Trajectory"])

# --- TAB 1: THE CLIMATE SPIRAL (Polar Plot) ---
with tab1:
    st.markdown("### Radial Temperature Evolution")
    st.write("Instead of a flat heatmap, we map months onto a 360° polar axis. As years progress, the radius expands, visualizing how recent years break outward from historical norms.")
    
    # Drop NaNs and convert Year to string for discrete colors
    df_melt_spiral = df_melt.dropna().copy()
    df_melt_spiral['Year_str'] = df_melt_spiral['Year'].astype(str)
    
    # render_mode="svg" fixes the WebGL shape/dash error!
    fig_spiral = px.line_polar(
        df_melt_spiral, r="Anomaly", theta="Month", color="Year_str",
        color_discrete_sequence=px.colors.sequential.Turbo, 
        template="plotly_dark", line_close=True,
        render_mode="svg" 
    )
    
    fig_spiral.update_traces(opacity=0.6, line=dict(width=1.5))
    fig_spiral.update_layout(
        height=700, 
        showlegend=False, 
        polar=dict(radialaxis=dict(visible=True, showticklabels=True))
    )
    st.plotly_chart(fig_spiral, use_container_width=True)


# --- TAB 2: SHADED VOLATILITY BANDS (Bollinger Bands for Climate) ---
with tab2:
    st.markdown("### Climate Volatility (Rolling Averages + Standard Deviation)")
    st.write("Does global warming mean higher extremes? This chart maps the moving average as a solid line, with the shaded area representing the statistical volatility (Standard Deviation).")
    
    df_annual['Rolling_Mean'] = df_annual['J-D'].rolling(window=roll_window).mean()
    df_annual['Rolling_Std'] = df_annual['J-D'].rolling(window=roll_window).std()
    df_annual['Upper_Band'] = df_annual['Rolling_Mean'] + df_annual['Rolling_Std']
    df_annual['Lower_Band'] = df_annual['Rolling_Mean'] - df_annual['Rolling_Std']

    fig_vol = go.Figure()
    # Add shaded uncertainty area
    fig_vol.add_trace(go.Scatter(
        x=pd.concat([df_annual['Year'], df_annual['Year'][::-1]]),
        y=pd.concat([df_annual['Upper_Band'], df_annual['Lower_Band'][::-1]]),
        fill='toself', fillcolor='rgba(255, 69, 0, 0.2)', line=dict(color='rgba(255,255,255,0)'),
        name=f'{roll_window}-Year Volatility Band'
    ))
    # Add Moving Average Line
    fig_vol.add_trace(go.Scatter(
        x=df_annual['Year'], y=df_annual['Rolling_Mean'],
        line=dict(color='#FF4500', width=3), name=f'{roll_window}-Year Average'
    ))
    # Add actual annual data points as faint dots
    fig_vol.add_trace(go.Scatter(
        x=df_annual['Year'], y=df_annual['J-D'],
        mode='markers', marker=dict(color='white', size=4, opacity=0.4), name='Actual Anomaly'
    ))
    
    fig_vol.update_layout(template="plotly_dark", height=600, hovermode="x unified", yaxis_title="Temperature Anomaly (°C)")
    st.plotly_chart(fig_vol, use_container_width=True)


# --- TAB 3: 3D PCA TRAJECTORY ---
with tab3:
    st.markdown("### 3D Dimensionality Reduction (PCA)")
    st.write("We've extracted a 3rd Principal Component. Watch how the climate 'cluster' fundamentally migrates through 3D mathematical space over the last century.")
    
    from sklearn.decomposition import PCA
    pca_3d = PCA(n_components=3)
    pca_data_3d = df_recal.dropna(subset=month_cols).copy()
    components_3d = pca_3d.fit_transform(pca_data_3d[month_cols])
    
    pca_data_3d['PC1'] = components_3d[:, 0]
    pca_data_3d['PC2'] = components_3d[:, 1]
    pca_data_3d['PC3'] = components_3d[:, 2]
    
    fig_3d = px.scatter_3d(
        pca_data_3d, x='PC1', y='PC2', z='PC3',
        color='Year', color_continuous_scale='Inferno',
        opacity=0.8, size_max=5
    )
    # Tweak the 3D axes to look sleek
    fig_3d.update_layout(
        template="plotly_dark", height=700,
        scene=dict(
            xaxis=dict(showbackground=False, title='PC1: Overall Trend'),
            yaxis=dict(showbackground=False, title='PC2: Volatility'),
            zaxis=dict(showbackground=False, title='PC3: Micro-Seasons')
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("👨‍💻 **Developed for Data Science Portfolio** | Built with Streamlit, Plotly Graph Objects, and Scikit-Learn.")
