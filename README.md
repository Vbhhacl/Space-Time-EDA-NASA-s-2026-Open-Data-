🚀 Space-Time EDA on NASA Open Data

This project presents a full-stack Exploratory Data Analysis (EDA) dashboard built using NASA’s open datasets, focusing on spatio-temporal patterns in global temperature data. It combines data preprocessing, analysis, and interactive visualization into a single streamlined application.

📌 Project Overview

The goal of this project is to analyze how temperature varies across time (years/months) and space (regions/global trends) using real-world NASA datasets. The system processes raw data, extracts meaningful insights, and presents them through an intuitive dashboard.

⚙️ Key Features
🔍 Data Preprocessing & Cleaning
Handles missing values and inconsistent formats
Transforms raw CSV data into structured format
📊 Exploratory Data Analysis (EDA)
Trend analysis of global temperatures over time
Seasonal and yearly variation insights
Statistical summaries and correlations
🌍 Spatio-Temporal Visualization
Time-series plots for temperature trends
Comparative analysis across different periods
Interactive charts for better understanding
💻 Full-Stack Implementation
Backend data engine for processing (data_engine.py)
Frontend dashboard for visualization (app.py)
Lightweight and easy to run locally
🛠️ Tech Stack
Python
Pandas & NumPy – Data processing
Matplotlib / Plotly / Streamlit (if used) – Visualization
Flask / Streamlit (depending on your app) – Web interface
📁 Dataset
Uses NASA open data (e.g., global temperature dataset)
File included: global_temps.csv
🎯 Use Cases
Climate trend analysis
Academic EDA projects
Data visualization practice
Understanding real-world spatio-temporal datasets
▶️ How to Run
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
📌 Future Enhancements
Add machine learning models for prediction
Integrate more NASA datasets
Deploy as a web application
Add advanced geospatial visualizations
