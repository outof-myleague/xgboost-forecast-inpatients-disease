This project uses the Extreme Gradient Boosting (XGBoost) algorithm to forecast the **top 10 most frequent inpatient diseases**, based on hospital admission data. The goal is to support healthcare management in predicting disease trends and optimizing hospital resources.

## Dataset
 `common_diseases.csv` is the main dataset used in this project. It contains daily historical records of inpatient cases grouped by ICD-10 disease codes.

 ## XGBoost Forecasting Model
 `xgboost-A09.ipynb`, `xgboost-D64.ipynb`... (and others up to the top 10 diseases) is the core of this project consists of individual XGBoost forecasting models. Each model is implemented in a separate Jupyter notebook.

 `predictions_A09_disease.csv,  ...` is the forecasted results for each disease that exported as CSV files for use in the dashboard.
 
 ## Dashboard Output
The final output of this research is the file  `dashboard_predicted.py`. A dashboard that visualizes the predicted trends of the top 10 inpatient diseases for the next 12 months.
