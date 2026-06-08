import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(page_title="Sales ERP Dashboard", layout="wide", page_icon="📊")

# Custom CSS for better styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #0f0a4f;
        padding: 10px;
        border-radius: 10px;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# LOAD DATA WITH CACHING
# -------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/transformed_clean_sales_data_2.csv")
        df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')
        # Drop rows with invalid dates
        df = df.dropna(subset=['OrderDate'])
        return df
    except FileNotFoundError:
        st.error("⚠️ Data file 'transformed_clean_sales_data_2.csv' not found!")
        st.stop()

df = load_data()

# -------------------------
# SIDEBAR FILTERS
# -------------------------
st.sidebar.title("🎛️ Dashboard Controls")

min_date = df['OrderDate'].min()
max_date = df['OrderDate'].max()

start_date, end_date = st.sidebar.date_input(
    "📅 Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Sales Executive filter
all_execs = ['All'] + sorted(df['SalesName'].unique().tolist())
selected_execs = st.sidebar.multiselect(
    "👨‍💼 Filter by Sales Executive",
    options=df['SalesName'].unique(),
    default=df['SalesName'].unique()
)

# Customer search
customer_search = st.sidebar.text_input("🔍 Search Customer", placeholder="Type customer iD (CUST00001)").upper()

# Apply filters
filtered_df = df[
    (df['OrderDate'] >= pd.to_datetime(start_date)) &
    (df['OrderDate'] <= pd.to_datetime(end_date)) &
    (df['SalesName'].isin(selected_execs))
]

if customer_search:
    filtered_df = filtered_df[filtered_df['CustomerID'].str.contains(customer_search, case=False, na=False)]

# -------------------------
# KPIs
# -------------------------
total_sales = filtered_df['SalesValue'].sum()
total_paid = filtered_df['CreditedAmount'].sum()
total_due = filtered_df['DueAmount'].sum()
customers = filtered_df['CustomerID'].nunique()
avg_order_value = filtered_df['SalesValue'].mean() if len(filtered_df) > 0 else 0
collection_rate = (total_paid / total_sales * 100) if total_sales > 0 else 0

st.title("📊 Sales ERP Dashboard")
st.markdown("---")

# KPI Row
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("💰 Total Sales", f"${total_sales:,.2f}", delta=None)
col2.metric("💵 Total Paid", f"${total_paid:,.2f}", delta=None)
col3.metric("⚠️ Total Due", f"${total_due:,.2f}", delta=None)
col4.metric("👥 Active Customers", f"{customers:,}", delta=None)
col5.metric("📊 Avg Order Value", f"${avg_order_value:,.2f}", delta=None)
col6.metric("✅ Collection Rate", f"{collection_rate:.1f}%", delta=None)

st.markdown("---")

# -------------------------
# TABS FOR ORGANIZED VIEW
# -------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview & Trends", "👤 Customer Analytics", "🧑‍💼 Executive Performance", "🔍 3D Analytics"])

# -------------------------
# TAB 1: Overview & Trends
# -------------------------
with tab1:
    # Monthly Sales Trend with Plotly
    st.subheader("📈 Monthly Sales Trend")
    filtered_df_month = filtered_df.copy()
    filtered_df_month['Month'] = filtered_df_month['OrderDate'].dt.to_period('M').astype(str)
    monthly_sales = filtered_df_month.groupby('Month')['SalesValue'].sum().reset_index()
    monthly_sales['Month'] = pd.to_datetime(monthly_sales['Month'])
    monthly_sales = monthly_sales.sort_values('Month')
    
    fig_trend = px.line(
        monthly_sales, x='Month', y='SalesValue',
        title='Monthly Sales Performance',
        markers=True, template='plotly_dark',
        labels={'SalesValue': 'Total Sales ($)', 'Month': 'Month'}
    )
    fig_trend.update_traces(line=dict(width=3, color='#00FFAA'), marker=dict(size=8))
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Sales by Executive (Bar Chart)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏆 Sales by Executive")
        exec_sales = filtered_df.groupby('SalesName')['SalesValue'].sum().reset_index().sort_values('SalesValue', ascending=True)
        fig_exec = px.bar(
            exec_sales, x='SalesValue', y='SalesName',
            orientation='h', title='Total Sales per Executive',
            color='SalesValue', color_continuous_scale='Viridis',
            template='plotly_white'
        )
        st.plotly_chart(fig_exec, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Collection Efficiency")
        exec_collection = filtered_df.groupby('SalesName').agg({
            'SalesValue': 'sum',
            'CreditedAmount': 'sum'
        }).reset_index()
        exec_collection['Collection_Rate'] = (exec_collection['CreditedAmount'] / exec_collection['SalesValue'] * 100).fillna(0)
        fig_collect = px.bar(
            exec_collection, x='SalesName', y='Collection_Rate',
            title='Collection Rate by Executive (%)',
            color='Collection_Rate', color_continuous_scale='RdYlGn',
            template='plotly_white'
        )
        st.plotly_chart(fig_collect, use_container_width=True)

# -------------------------
# TAB 2: Customer Analytics (Includes Bubble Chart)
# -------------------------
with tab2:
    st.subheader("👤 Customer Performance Analysis")
    
    # Customer aggregation
    customer_report = (
        filtered_df.groupby(['CustomerName', 'CustomerID'])
        .agg({
            'SalesValue': 'sum',
            'CreditedAmount': 'sum',
            'SalesReturn': 'sum',
            'DueAmount': 'sum'
        })
        .reset_index()
    )
    
    customer_report['NetSales'] = customer_report['SalesValue'] - customer_report['SalesReturn']
    customer_report['Outstanding'] = customer_report['NetSales'] - customer_report['CreditedAmount']
    customer_report['Return_Rate'] = (customer_report['SalesReturn'] / customer_report['SalesValue'] * 100).fillna(0)
    
    # Top customers selection
    top_n = st.slider("Select number of top customers to display", 5, 30, 15)
    top_customers = customer_report.nlargest(top_n, 'SalesValue')
    
    # BUBBLE CHART: Sales Value vs Outstanding with bubble size = Sales Return
    st.subheader("🫧 Customer Bubble Chart (Sales Value vs Outstanding)")
    fig_bubble = px.scatter(
        top_customers,
        x='SalesValue',
        y='Outstanding',
        size='SalesReturn',
        color='CustomerName',
        hover_name='CustomerName',
        size_max=60,
        title=f'Top {top_n} Customers: Sales vs Outstanding (Bubble Size = Returns)',
        labels={'SalesValue': 'Total Sales ($)', 'Outstanding': 'Outstanding Amount ($)'},
        template='plotly_dark'
    )
    fig_bubble.update_layout(showlegend=False, height=600)
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # Customer Data Table
    st.subheader("📋 Customer Detailed Report")
    st.dataframe(
        customer_report[['CustomerName', 'CustomerID', 'SalesValue', 'CreditedAmount', 'SalesReturn', 'NetSales', 'Outstanding', 'Return_Rate']]
        .sort_values('SalesValue', ascending=False)
        .style.format({
            'SalesValue': '${:,.2f}',
            'CreditedAmount': '${:,.2f}',
            'SalesReturn': '${:,.2f}',
            'NetSales': '${:,.2f}',
            'Outstanding': '${:,.2f}',
            'Return_Rate': '{:.1f}%'
        })
    )
    
    # Outstanding Customers (Bar Chart)
    st.subheader("⚠️ Top Outstanding Customers")
    top_outstanding = customer_report.nlargest(10, 'Outstanding')
    fig_outstanding = px.bar(
        top_outstanding,
        x='Outstanding',
        y='CustomerName',
        orientation='h',
        title='Customers with Highest Outstanding Amount',
        color='Outstanding',
        color_continuous_scale='Reds',
        template='plotly_white'
    )
    st.plotly_chart(fig_outstanding, use_container_width=True)

# -------------------------
# TAB 3: Executive Performance & 3D Bubble Chart
# -------------------------
with tab3:
    st.subheader("🧑‍💼 Sales Executive Dashboard")
    
    # Executive aggregation
    exec_report = (
        filtered_df.groupby('SalesName')
        .agg({
            'SalesValue': 'sum',
            'CreditedAmount': 'sum',
            'DueAmount': 'sum',
            'SalesReturn': 'sum',
            'InvoiceNo': 'count'  # Number of transactions
        })
        .reset_index()
    )
    exec_report.rename(columns={'InvoiceNo': 'TransactionCount'}, inplace=True)
    exec_report['NetSales'] = exec_report['SalesValue'] - exec_report['SalesReturn']
    exec_report['Collection_Rate'] = (exec_report['CreditedAmount'] / exec_report['SalesValue'] * 100).fillna(0)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.dataframe(
            exec_report[['SalesName', 'SalesValue', 'CreditedAmount', 'DueAmount', 'TransactionCount', 'Collection_Rate']]
            .sort_values('SalesValue', ascending=False)
            .style.format({
                'SalesValue': '${:,.2f}',
                'CreditedAmount': '${:,.2f}',
                'DueAmount': '${:,.2f}',
                'Collection_Rate': '{:.1f}%'
            })
        )
    
    with col2:
        # 3D BUBBLE CHART for Executives
        st.subheader("🎨 3D Executive Performance Bubble Chart")
        fig_3d_bubble = go.Figure(data=[go.Scatter3d(
            x=exec_report['SalesValue'],
            y=exec_report['CreditedAmount'],
            z=exec_report['DueAmount'],
            mode='markers+text',
            marker=dict(
                size=exec_report['TransactionCount'] / exec_report['TransactionCount'].max() * 50 + 10,
                color=exec_report['Collection_Rate'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Collection Rate %"),
                opacity=0.8,
                line=dict(width=1, color='black')
            ),
            text=exec_report['SalesName'],
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>" +
                          "Sales: $%{x:,.0f}<br>" +
                          "Paid: $%{y:,.0f}<br>" +
                          "Due: $%{z:,.0f}<br>" +
                          "Collection Rate: %{marker.color:.1f}%<br>" +
                          "Transactions: %{marker.size:.0f}<extra></extra>"
        )])
        
        fig_3d_bubble.update_layout(
            scene=dict(
                xaxis_title="Total Sales ($)",
                yaxis_title="Total Paid ($)",
                zaxis_title="Total Due ($)",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=600,
            title_text="3D Performance Matrix: Sales vs Paid vs Due",
            template='plotly_dark'
        )
        st.plotly_chart(fig_3d_bubble, use_container_width=True)

# -------------------------
# TAB 4: Advanced 3D Analytics
# -------------------------
with tab4:
    st.subheader("🔬 Advanced 3D Analytics")
    
    # Prepare daily aggregated data for 3D scatter
    daily_data = filtered_df.groupby(filtered_df['OrderDate'].dt.date).agg({
        'SalesValue': 'sum',
        'CreditedAmount': 'sum',
        'DueAmount': 'sum',
        'CustomerID': 'nunique'
    }).reset_index()
    daily_data.columns = ['Date', 'DailySales', 'DailyPaid', 'DailyDue', 'UniqueCustomers']
    
    # 3D Scatter Plot: Daily Sales, Paid, Due
    fig_3d_daily = go.Figure(data=[go.Scatter3d(
        x=daily_data['DailySales'],
        y=daily_data['DailyPaid'],
        z=daily_data['DailyDue'],
        mode='markers',
        marker=dict(
            size=daily_data['UniqueCustomers'] / daily_data['UniqueCustomers'].max() * 30 + 5,
            color=daily_data['DailySales'],
            colorscale='Plasma',
            showscale=True,
            colorbar=dict(title="Daily Sales ($)"),
            opacity=0.7
        ),
        text=daily_data['Date'].astype(str),
        hovertemplate="<b>Date: %{text}</b><br>" +
                      "Sales: $%{x:,.0f}<br>" +
                      "Paid: $%{y:,.0f}<br>" +
                      "Due: $%{z:,.0f}<br>" +
                      "Unique Customers: %{marker.size:.0f}<extra></extra>"
    )])
    
    fig_3d_daily.update_layout(
        scene=dict(
            xaxis_title="Daily Sales ($)",
            yaxis_title="Daily Paid ($)",
            zaxis_title="Daily Due ($)",
            camera=dict(eye=dict(x=2, y=1.5, z=1.2))
        ),
        height=700,
        title_text="📊 3D Daily Performance: Sales, Payments, and Outstanding Amounts",
        template='plotly_white'
    )
    st.plotly_chart(fig_3d_daily, use_container_width=True)
    
    # Additional: Sales vs Returns 3D
    st.subheader("🔄 Sales vs Returns Analysis")
    returns_data = filtered_df.groupby(filtered_df['OrderDate'].dt.date).agg({
        'SalesValue': 'sum',
        'SalesReturn': 'sum'
    }).reset_index()
    returns_data = returns_data[returns_data['SalesReturn'] > 0]
    
    if len(returns_data) > 0:
        fig_returns_3d = px.scatter_3d(
            returns_data,
            x='SalesValue',
            y='SalesReturn',
            z='OrderDate',
            color='SalesValue',
            size='SalesReturn',
            title='3D View: Sales vs Returns Over Time',
            labels={'SalesValue': 'Sales ($)', 'SalesReturn': 'Returns ($)', 'OrderDate': 'Date'},
            color_continuous_scale='RdYlGn_r',
            template='plotly_dark'
        )
        st.plotly_chart(fig_returns_3d, use_container_width=True)
    else:
        st.info("No return transactions in the selected date range.")
    
    # Download filtered data
    st.subheader("📥 Export Data")
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data as CSV",
        data=csv,
        file_name="filtered_sales_data.csv",
        mime="text/csv",
    )

# Footer
st.markdown("---")
st.caption(f"📅 Data Period: {start_date} to {end_date} | Total Records: {len(filtered_df):,} | Dashboard built with ❤️ using Streamlit & Plotly")


st.markdown("""
    <div class="copyright-footer">
        <div class="footer-content">
            <span class="copyright-text">© 2026 Sales ERP Dashboard | All Rights Reserved</span>
            <span>Made with <span class="heart">❤️</span> Mujakkr Ahmad</span>
            <span>
                <a href="#" target="_blank">Privacy</a> | 
                <a href="#" target="_blank">Terms</a>
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)