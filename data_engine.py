import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def load_and_clean_data(filepath):
    """Loads NASA dataset and handles historical and recent missing values."""
    df = pd.read_csv(filepath)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for col in months:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna(subset=['Jan', 'Feb', 'Mar']) 
    return df, months

def recalibrate_baseline(df, months, start_year=1880, end_year=1900):
    """Recalibrates temperature anomalies to a user-selected baseline."""
    df_copy = df.copy()
    baseline_data = df_copy[(df_copy['Year'] >= start_year) & (df_copy['Year'] <= end_year)]
    monthly_baselines = baseline_data[months].mean()
    
    for month in months:
        df_copy[month] = df_copy[month] - monthly_baselines[month]
        
    return df_copy

def run_pca_on_seasons(df, months):
    """Runs Principal Component Analysis (PCA) to find hidden seasonal shifts."""
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
    df_copy['Annual_Volatility'] = df_copy['J-D'].rolling(window=window).std()
    return df_copy
def generate_prediction(df, future_year):
    """Trains a polynomial regression model to predict future anomalies."""
    clean_df = df[['Year', 'J-D']].dropna()
    X = clean_df[['Year']].values
    y = clean_df['J-D'].values
    
    # We use a 2nd-degree polynomial to capture the accelerating curve
    poly = PolynomialFeatures(degree=2)
    X_poly = poly.fit_transform(X)
    
    model = LinearRegression()
    model.fit(X_poly, y)
    
    # Predict the specific target year
    future_X = np.array([[future_year]])
    future_X_poly = poly.transform(future_X)
    prediction = model.predict(future_X_poly)[0]
    
    # Generate the trendline for the chart (from 1880 up to the future year)
    future_years = np.arange(int(X.min()), future_year + 1).reshape(-1, 1)
    future_years_poly = poly.transform(future_years)
    trend_y = model.predict(future_years_poly)
    
    trend_df = pd.DataFrame({'Year': future_years.flatten(), 'Predicted_Anomaly': trend_y})
    
    return prediction, trend_df