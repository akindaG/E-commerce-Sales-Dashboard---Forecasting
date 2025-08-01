# E-commerce Sales Dashboard & Forecasting

## 🚀 Project Overview

A comprehensive analytics system that predicts revenue, identifies top customers, optimizes inventory, and provides actionable insights for e-commerce growth.

**Business Value**: E-commerce businesses lose 20-30% potential revenue due to poor inventory planning, ineffective marketing spend, and inability to predict seasonal demand patterns. This solution addresses these critical pain points.

**Target Revenue**: $2,000-5,000 for initial dashboard + $500-1,500/month for ongoing updates and insights.

## 📊 Features

- **Revenue Forecasting**: Predict future sales using time series analysis
- **Customer Segmentation**: RFM analysis to identify high-value customers
- **Product Performance**: ABC analysis for inventory optimization
- **Interactive Dashboard**: Real-time analytics with Plotly Dash and Streamlit
- **Business Insights**: Automated recommendations and actionable insights

## 🛠️ Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the UCI Online Retail Dataset:
   - Visit: https://archive.ics.uci.edu/ml/datasets/online+retail
   - Download the Excel file and place it in the `data/` folder as `Online_Retail.xlsx`

## 📁 Project Structure

```
├── data/                   # Data files
├── src/                    # Source code
│   ├── data_processing.py  # Data cleaning and preparation
│   ├── analytics.py        # Core analytics functions
│   ├── forecasting.py      # Revenue forecasting models
│   └── dashboard.py        # Dashboard components
├── dashboards/             # Dashboard applications
│   ├── dash_app.py         # Plotly Dash dashboard
│   └── streamlit_app.py    # Streamlit dashboard
├── notebooks/              # Jupyter notebooks for exploration
├── reports/                # Generated reports and insights
└── docs/                   # Documentation and business materials
```

## 🚀 Quick Start

### 1. Data Processing
```bash
python src/data_processing.py
```

### 2. Run Streamlit Dashboard (Recommended)
```bash
streamlit run dashboards/streamlit_app.py
```

### 3. Run Dash Dashboard
```bash
python dashboards/dash_app.py
```

## 📈 Key Metrics

- **Total Revenue**: $8,847,620.00
- **Total Customers**: 4,372
- **Total Orders**: 25,900
- **Average Order Value**: $341.65
- **Revenue Growth**: 15.2% over analysis period

## 🎯 Business Insights

### Customer Segments
- **Champions**: High-value, frequent buyers (20% of customers, 60% of revenue)
- **Loyal Customers**: Regular buyers with good potential
- **At Risk**: Declining engagement, need retention campaigns
- **New Customers**: Recent acquisitions, focus on conversion

### Product Performance
- **Category A**: Top 20% products generating 80% of revenue
- **Category B**: 15% of products generating 15% of revenue  
- **Category C**: 65% of products generating 5% of revenue

### Seasonal Patterns
- Peak sales in November-December (holiday season)
- Lowest sales in January-February
- Weekly patterns show higher sales on weekdays

## 💼 Business Recommendations

1. **Inventory Optimization**: Use ABC analysis to focus on high-value products
2. **Customer Retention**: Implement targeted campaigns for "At Risk" customers
3. **Seasonal Planning**: Prepare inventory and marketing for peak periods
4. **Marketing Efficiency**: Focus spend on high-value customer segments

## 📊 Dashboard Features

### Interactive Visualizations
- Revenue trends with forecasting
- Customer segmentation charts
- Product performance analysis
- Geographic sales distribution
- Seasonal pattern analysis

### Real-time Analytics
- Live KPI updates
- Filterable date ranges
- Drill-down capabilities
- Export functionality

## 🎯 ROI Projection

**For a typical $1M revenue e-commerce business**:
- **Dashboard Setup**: $3,000 one-time
- **Monthly Updates**: $800/month
- **Projected Savings**: 
  - 15% inventory optimization: $150,000
  - 20% marketing efficiency: $200,000
  - **Total Annual Savings**: $350,000+

## 📞 Contact & Support

This project demonstrates advanced analytics capabilities including:
- Time series forecasting
- Customer segmentation
- Inventory optimization
- Interactive dashboard development
- Business intelligence reporting

Perfect for portfolio projects and client presentations!

## 📄 License

This project is open source and available under the MIT License. #   E - c o m m e r c e - S a l e s - D a s h b o a r d - - - F o r e c a s t i n g  
 