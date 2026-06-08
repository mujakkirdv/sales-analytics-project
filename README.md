# Sales Analytics & ERP Dashboard (Python + Streamlit)

A complete business intelligence and ERP-style analytics system built using Python, Pandas, Matplotlib, Seaborn, and Streamlit.  
This project converts raw sales data into a structured dataset with customer management, executive tracking, and interactive dashboard reporting.

---

## Project Overview

This project focuses on transforming raw sales data into a clean analytical system with the following capabilities:

- Data cleaning and preprocessing
- Unique customer ID generation system
- Sales executive performance analysis
- Customer-wise sales, payment, and due tracking
- Time-based sales analysis
- Interactive Streamlit dashboard
- Machine learning ready dataset structure

---

## Features

### Data Engineering
- Handle missing values
- Standardize date formats
- Convert numeric columns
- Clean inconsistent data entries

### Customer Management System
- Generate unique CustomerID for each customer
- Maintain customer master table
- Track customer behavior and purchase history
- Calculate outstanding dues per customer

### Sales Analytics
- Total sales analysis
- Net sales calculation
- Discount and return tracking
- Commission tracking
- Due amount calculation

### Executive Performance
- Sales by each sales executive
- Collection performance tracking
- Customer distribution per executive

### Time Series Analysis
- Daily, monthly, and yearly trends
- Seasonal sales performance
- Revenue trend analysis

### Dashboard
Interactive Streamlit dashboard includes:
- Date range filter
- Customer filter
- Executive filter
- KPI summary cards
- Charts and tables

---

## Project Structure
sales-analytics-project/
│
├── data/
│ └── clean_sales_data.csv
│
├── app.py
├── analysis.ipynb
├── README.md



---

## Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/mujakkirdv/sales-analytics-project.git
cd sales-analytics-project

## Step 2: Install Dependencies
pip install pandas numpy matplotlib seaborn streamlit

Run Streamlit Dashboard
streamlit run app.py

Key Business Metrics
Total Sales
Total Collection
Total Outstanding Due
Unique Customers
Sales Executive Performance
Monthly Sales Trends
Visual Analysis
Top customers by sales
Top sales executives
Outstanding customers
Monthly sales trend
Sales distribution
Correlation analysis
Machine Learning Use Cases

This dataset can be used for:

Sales forecasting models
Customer segmentation (RFM analysis)
Payment default prediction
Revenue prediction models
Technology Stack
Python
Pandas
NumPy
Matplotlib
Seaborn
Streamlit
Scikit-learn (for ML models)
Future Improvements
Authentication system for multi-user access
Invoice generation module
Inventory management system
API backend using FastAPI or Django
Cloud deployment (AWS / Render / Streamlit Cloud)
Author

Mujakkir Ahmad
Data Analyst | Python Developer | ERP & Analytics Systems Developer


---