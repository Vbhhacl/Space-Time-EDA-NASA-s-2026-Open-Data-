import pandas as pd
import numpy as np
from sklearn.decomposition import PCA

def load_and_clean_data(filepath):
    """Loads NASA dataset and handles historical and recent missing values."""
    df = pd.read_csv(filepath)
    
    # Isolate just the month columns
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Handle the 2023 missing data 
    for col in months:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows where the whole year is basically NaN (if any extreme cases)
    df = df.dropna(subset=['Jan', 'Feb', 'Mar']) 
    
    return df, months

def recalibrate_baseline(df, months, start_year=1880, end_year=1900):
    """
    Recalibrates the temperature anomalies from the NASA mid-century baseline 
    to a pre-industrial baseline (e.g., 1880-1900).
    """
    df_copy = df.copy()
    
    # Calculate the average temperature for each month during the baseline period
    baseline_data = df_copy[(df_copy['Year'] >= start_year) & (df_copy['Year'] <= end_year)]
    monthly_baselines = baseline_data[months].mean()
    
    # Subtract this baseline from the entire dataset to recalibrate
    for month in months:
        df_copy[month] = df_copy[month] - monthly_baselines[month]
        
    return df_copy

def run_pca_on_seasons(df, months):
    """
    Runs Principal Component Analysis (PCA) to find hidden seasonal shifts.
    """
    # Drop rows with NaN for PCA to work mathematically
    pca_data = df.dropna(subset=months).copy()
    
    pca = PCA(n_components=2)
    components = pca.fit_transform(pca_data[months])
    
    pca_data['PCA_1 (Overall Trend)'] = components[:, 0]
    pca_data['PCA_2 (Seasonal Volatility)'] = components[:, 1]
    
    variance_explained = pca.explained_variance_ratio_
    
    return pca_data, variance_explained

def calculate_volatility(df, window=10):
    """Calculates the rolling standard deviation (volatility) of annual temps."""
    df_copy = df.copy()
    # Using J-D (January-December Annual Average)
    df_copy['Annual_Volatility'] = df_copy['J-D'].rolling(window=window).std()
    return df_copy