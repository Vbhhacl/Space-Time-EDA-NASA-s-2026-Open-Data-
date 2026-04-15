# 🌍 Space-Time EDA: Climate Acceleration & Volatility Signatures

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-FF4B4B.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.19.0-3F4F75.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.4.1-F7931E.svg)
![Data](https://img.shields.io/badge/Data-NASA_GISTEMP-black.svg)

An advanced, full-stack Exploratory Data Analysis (EDA) dashboard built to recalibrate, analyze, and visualize over a century of global temperature anomalies using spatial-temporal data from NASA.

## 📌 Project Overview
Most climate data analysis focuses on a simple linear trend of warming. This project goes deeper by treating climate data as a highly volatile time-series dataset. Instead of relying on static, mid-century baselines, this application allows users to **mathematically recalibrate the dataset to pre-industrial baselines** dynamically. 

Furthermore, it applies dimensionality reduction (PCA) and rolling statistical methods to prove that an increase in global temperature directly correlates with an increase in **seasonal unpredictability and mathematical volatility**.

### 🎯 Key Analytical Features
* **Dynamic Baseline Recalibration:** Real-time matrix transformation to shift NASA's default baseline (1951-1980) to user-defined pre-industrial periods (e.g., 1880-1900).
* **The Global Warming Stripes:** Implementation of Prof. Ed Hawkins' famous chronological heatmap barcode.
* **The Climate Spiral (Polar EDA):** A 360° radial time-series visualization mapping the outward expansion of temperature anomalies.
* **Statistical Volatility Bands:** A financial-style "Bollinger Band" analysis applying rolling moving averages and standard deviations to measure extreme climate deviations.
* **3D Principal Component Analysis (PCA):** Extracts multi-dimensional seasonal signatures to map the fundamental trajectory shift of the global climate cluster through 3D mathematical space.

## 🏗️ Tech Stack & Architecture
This project separates the heavy data engineering logic from the frontend UI to maintain production-level software architecture.

* **Frontend:** Streamlit (UI/UX routing)
* **Visualizations:** Plotly Express & Plotly Graph Objects (SVG/WebGL rendering)
* **Data Engineering (Backend):** Pandas & NumPy
* **Machine Learning / Math:** Scikit-Learn (PCA)

## 📂 Project Structure
```text
├── app.py                 # Streamlit frontend, UI layout, and Plotly visualizations
├── data_engine.py         # Backend logic, missing value handling, PCA, and statistics
├── global_temps.csv       # Raw NASA GISTEMP dataset (1880 - 2023)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 📊 Data Source
The data used in this project is sourced from the **NASA GISS Surface Temperature Analysis (GISTEMP v4)**. It contains monthly global surface temperature anomaly data from 1880 to the present.

## 🚀 How to Run Locally

### 1. Clone the Repository
```bash
git clone [https://github.com/Vbhhacl/Space-Time-EDA-NASA-s-2026-Open-Data-.git](https://github.com/Vbhhacl/Space-Time-EDA-NASA-s-2026-Open-Data-.git)
cd Space-Time-EDA-NASA-s-2026-Open-Data-
```

### 2. Install Dependencies
It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
The application will automatically open in your default web browser at http://localhost:8501.

## ☁️ Running in GitHub Codespaces

 *  This project is fully optimized for cloud development via GitHub Codespaces.
  
 *  Click the Code button on the repository and select Open with Codespaces.
  
 *  Once the Codespace boots up, open the terminal.
  
 *  Run pip install -r requirements.txt.
  
 *  Run streamlit run app.py.
  
  * Click "Open in Browser" on the port forwarding notification (Port 8501) in the bottom right corner.
