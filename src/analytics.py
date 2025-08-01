"""
Analytics Module for E-commerce Analytics
Handles RFM analysis, customer segmentation, and product performance
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EcommerceAnalytics:
    def __init__(self, data_processor=None):
        """
        Initialize the analytics module
        
        Args:
            data_processor: EcommerceDataProcessor instance with cleaned data
        """
        self.data_processor = data_processor
        self.rfm_data = None
        self.product_abc = None
        
    def perform_rfm_analysis(self, reference_date=None):
        """
        Perform RFM (Recency, Frequency, Monetary) analysis
        
        Args:
            reference_date: Reference date for recency calculation (default: max date + 1 day)
        """
        if self.data_processor is None or self.data_processor.cleaned_df is None:
            print("[ERROR] No data available. Please provide data processor with cleaned data.")
            return None
            
        df = self.data_processor.cleaned_df
        
        # Set reference date
        if reference_date is None:
            reference_date = df['InvoiceDate'].max() + timedelta(days=1)
        
        # Calculate RFM metrics
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
            'InvoiceNo': 'nunique',  # Frequency
            'TotalPrice': 'sum'  # Monetary
        }).reset_index()
        
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        
        # Create RFM scores (1-5, where 5 is best)
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])
        
        # Combine scores
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
        
        # Calculate RFM score as numeric
        rfm['RFM_Score_Num'] = rfm['R_Score'].astype(int) + rfm['F_Score'].astype(int) + rfm['M_Score'].astype(int)
        
        # Segment customers
        rfm['Segment'] = rfm['RFM_Score'].apply(self._segment_customers)
        
        # Add additional metrics
        rfm['Avg_Order_Value'] = rfm['Monetary'] / rfm['Frequency']
        rfm['Customer_Lifetime_Value'] = rfm['Monetary'] * rfm['Frequency']
        
        self.rfm_data = rfm
        
        print(f"[OK] RFM analysis completed for {len(rfm)} customers")
        print(f"[INFO] Customer segments: {rfm['Segment'].value_counts().to_dict()}")
        
        return rfm
    
    def _segment_customers(self, rfm_score):
        """Define customer segments based on RFM score"""
        if rfm_score in ['555', '554', '544', '545', '454', '455', '445']:
            return 'Champions'
        elif rfm_score in ['543', '444', '435', '355', '354', '345', '344', '335']:
            return 'Loyal Customers'
        elif rfm_score in ['512', '511', '422', '421', '412', '411', '311']:
            return 'Potential Loyalists'
        elif rfm_score in ['155', '154', '144', '214', '215', '115', '114']:
            return 'New Customers'
        elif rfm_score in ['331', '321', '231', '241', '251']:
            return 'At Risk'
        elif rfm_score in ['111', '112', '113', '114', '115']:
            return 'Lost'
        else:
            return 'Others'
    
    def get_customer_insights(self):
        """Generate customer insights and recommendations"""
        if self.rfm_data is None:
            print("[ERROR] No RFM data available. Please perform RFM analysis first.")
            return None
            
        rfm = self.rfm_data
        
        insights = {
            'total_customers': len(rfm),
            'segment_distribution': rfm['Segment'].value_counts().to_dict(),
            'avg_customer_value': rfm['Monetary'].mean(),
            'top_segment': rfm['Segment'].value_counts().index[0],
            'champions_count': len(rfm[rfm['Segment'] == 'Champions']),
            'at_risk_count': len(rfm[rfm['Segment'] == 'At Risk']),
            'lost_count': len(rfm[rfm['Segment'] == 'Lost']),
            'repeat_customer_rate': (rfm[rfm['Frequency'] > 1].shape[0] / rfm.shape[0]) * 100
        }
        
        # Calculate segment value
        segment_value = rfm.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)
        insights['segment_value'] = segment_value.to_dict()
        
        # Generate recommendations
        recommendations = []
        
        if insights['champions_count'] > 0:
            champions_value = segment_value.get('Champions', 0)
            champions_pct = (champions_value / rfm['Monetary'].sum()) * 100
            recommendations.append(f"Champions generate {champions_pct:.1f}% of revenue - focus on retention and upselling")
        
        if insights['at_risk_count'] > 0:
            recommendations.append(f"At Risk customers ({insights['at_risk_count']}) need immediate attention - implement retention campaigns")
        
        if insights['lost_count'] > 0:
            recommendations.append(f"Lost customers ({insights['lost_count']}) - consider re-engagement campaigns")
        
        if insights['repeat_customer_rate'] < 50:
            recommendations.append(f"Repeat customer rate is {insights['repeat_customer_rate']:.1f}% - implement loyalty programs")
        
        insights['recommendations'] = recommendations
        
        return insights
    
    def perform_abc_analysis(self):
        """Perform ABC analysis for inventory optimization"""
        if self.data_processor is None or self.data_processor.cleaned_df is None:
            print("[ERROR] No data available. Please provide data processor with cleaned data.")
            return None
            
        df = self.data_processor.cleaned_df
        
        # Aggregate product data
        product_data = df.groupby(['StockCode', 'Description']).agg({
            'Quantity': 'sum',
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        product_data.columns = ['StockCode', 'Description', 'Total_Quantity', 'Total_Revenue', 'Order_Count', 'Customer_Count']
        product_data['Avg_Price'] = product_data['Total_Revenue'] / product_data['Total_Quantity']
        
        # Sort by revenue
        product_data = product_data.sort_values('Total_Revenue', ascending=False)
        
        # Calculate cumulative percentages
        product_data['Cumulative_Revenue'] = product_data['Total_Revenue'].cumsum()
        product_data['Revenue_Percentage'] = (product_data['Cumulative_Revenue'] / product_data['Total_Revenue'].sum()) * 100
        
        # Assign ABC categories
        product_data['ABC_Category'] = 'C'
        product_data.loc[product_data['Revenue_Percentage'] <= 80, 'ABC_Category'] = 'A'
        product_data.loc[(product_data['Revenue_Percentage'] > 80) & (product_data['Revenue_Percentage'] <= 95), 'ABC_Category'] = 'B'
        
        # Calculate category statistics
        abc_stats = product_data.groupby('ABC_Category').agg({
            'StockCode': 'count',
            'Total_Revenue': 'sum',
            'Total_Quantity': 'sum'
        }).reset_index()
        
        abc_stats.columns = ['Category', 'Product_Count', 'Total_Revenue', 'Total_Quantity']
        abc_stats['Revenue_Percentage'] = (abc_stats['Total_Revenue'] / abc_stats['Total_Revenue'].sum()) * 100
        abc_stats['Product_Percentage'] = (abc_stats['Product_Count'] / abc_stats['Product_Count'].sum()) * 100
        
        self.product_abc = product_data
        
        print("[OK] ABC analysis completed")
        print(f"[INFO] Category A: {abc_stats[abc_stats['Category'] == 'A']['Product_Count'].iloc[0]} products, {abc_stats[abc_stats['Category'] == 'A']['Revenue_Percentage'].iloc[0]:.1f}% of revenue")
        print(f"[INFO] Category B: {abc_stats[abc_stats['Category'] == 'B']['Product_Count'].iloc[0]} products, {abc_stats[abc_stats['Category'] == 'B']['Revenue_Percentage'].iloc[0]:.1f}% of revenue")
        print(f"[INFO] Category C: {abc_stats[abc_stats['Category'] == 'C']['Product_Count'].iloc[0]} products, {abc_stats[abc_stats['Category'] == 'C']['Revenue_Percentage'].iloc[0]:.1f}% of revenue")
        
        return product_data, abc_stats
    
    def get_seasonal_patterns(self):
        """Analyze seasonal patterns in sales"""
        if self.data_processor is None or self.data_processor.cleaned_df is None:
            print("[ERROR] No data available. Please provide data processor with cleaned data.")
            return None
            
        df = self.data_processor.cleaned_df
        
        # Monthly patterns
        monthly_patterns = df.groupby(['Year', 'Month', 'MonthName']).agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        # Day of week patterns
        dow_patterns = df.groupby(['DayOfWeek', 'DayName']).agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        # Hour patterns
        hour_patterns = df.groupby('Hour').agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        # Find peak periods
        peak_month = monthly_patterns.loc[monthly_patterns['TotalPrice'].idxmax()]
        peak_day = dow_patterns.loc[dow_patterns['TotalPrice'].idxmax()]
        peak_hour = hour_patterns.loc[hour_patterns['TotalPrice'].idxmax()]
        
        seasonal_insights = {
            'monthly_patterns': monthly_patterns,
            'dow_patterns': dow_patterns,
            'hour_patterns': hour_patterns,
            'peak_month': peak_month['MonthName'],
            'peak_day': peak_day['DayName'],
            'peak_hour': peak_hour['Hour'],
            'seasonality_score': self._calculate_seasonality_score(monthly_patterns)
        }
        
        return seasonal_insights
    
    def _calculate_seasonality_score(self, monthly_patterns):
        """Calculate seasonality score based on variance in monthly sales"""
        if len(monthly_patterns) < 2:
            return 0
        
        revenue_std = monthly_patterns['TotalPrice'].std()
        revenue_mean = monthly_patterns['TotalPrice'].mean()
        
        if revenue_mean == 0:
            return 0
        
        # Coefficient of variation
        cv = revenue_std / revenue_mean
        
        # Normalize to 0-100 scale
        seasonality_score = min(cv * 100, 100)
        
        return seasonality_score
    
    def get_geographic_analysis(self):
        """Analyze sales by country/region"""
        if self.data_processor is None or self.data_processor.cleaned_df is None:
            print("[ERROR] No data available. Please provide data processor with cleaned data.")
            return None
            
        df = self.data_processor.cleaned_df
        
        # Country analysis
        country_analysis = df.groupby('Country').agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        country_analysis.columns = ['Country', 'Total_Revenue', 'Orders', 'Customers', 'Quantity']
        country_analysis['Avg_Order_Value'] = country_analysis['Total_Revenue'] / country_analysis['Orders']
        country_analysis['Revenue_Percentage'] = (country_analysis['Total_Revenue'] / country_analysis['Total_Revenue'].sum()) * 100
        
        # Sort by revenue
        country_analysis = country_analysis.sort_values('Total_Revenue', ascending=False)
        
        return country_analysis
    
    def generate_business_report(self):
        """Generate comprehensive business insights report"""
        if self.rfm_data is None:
            print("[ERROR] No RFM data available. Please perform RFM analysis first.")
            return None
            
        # Get all insights
        customer_insights = self.get_customer_insights()
        seasonal_insights = self.get_seasonal_patterns()
        geographic_analysis = self.get_geographic_analysis()
        
        if self.data_processor:
            kpis = self.data_processor.calculate_kpis()
        else:
            kpis = None
        
        # Compile report
        report = {
            'executive_summary': {
                'total_revenue': kpis['total_revenue'] if kpis else 0,
                'total_customers': kpis['total_customers'] if kpis else 0,
                'revenue_growth': kpis['revenue_growth_pct'] if kpis else 0,
                'avg_order_value': kpis['avg_order_value'] if kpis else 0
            },
            'customer_insights': customer_insights,
            'seasonal_patterns': seasonal_insights,
            'geographic_analysis': geographic_analysis,
            'recommendations': self._generate_strategic_recommendations(customer_insights, seasonal_insights)
        }
        
        return report
    
    def _generate_strategic_recommendations(self, customer_insights, seasonal_insights):
        """Generate strategic business recommendations"""
        recommendations = []
        
        if customer_insights:
            # Customer-focused recommendations
            if customer_insights['champions_count'] > 0:
                recommendations.append({
                    'category': 'Customer Retention',
                    'priority': 'High',
                    'recommendation': 'Implement VIP programs for Champions segment',
                    'expected_impact': 'Increase customer lifetime value by 15-20%'
                })
            
            if customer_insights['at_risk_count'] > 0:
                recommendations.append({
                    'category': 'Customer Recovery',
                    'priority': 'High',
                    'recommendation': 'Launch targeted re-engagement campaigns for At Risk customers',
                    'expected_impact': 'Recover 20-30% of at-risk customers'
                })
        
        if seasonal_insights:
            # Seasonal recommendations
            if seasonal_insights['seasonality_score'] > 30:
                recommendations.append({
                    'category': 'Inventory Management',
                    'priority': 'Medium',
                    'recommendation': f'Prepare inventory for peak sales in {seasonal_insights["peak_month"]}',
                    'expected_impact': 'Reduce stockouts and increase sales by 10-15%'
                })
        
        # General recommendations
        recommendations.extend([
            {
                'category': 'Marketing Optimization',
                'priority': 'Medium',
                'recommendation': 'Focus marketing spend on high-value customer segments',
                'expected_impact': 'Improve marketing ROI by 25-35%'
            },
            {
                'category': 'Product Strategy',
                'priority': 'Low',
                'recommendation': 'Review and optimize Category C products',
                'expected_impact': 'Reduce inventory costs and improve efficiency'
            }
        ])
        
        return recommendations

def main():
    """Main function to demonstrate analytics capabilities"""
    from data_processing import EcommerceDataProcessor
    
    # Initialize data processor
    processor = EcommerceDataProcessor()
    
    # Load and clean data
    processor.load_data()
    processor.clean_data()
    
    # Initialize analytics
    analytics = EcommerceAnalytics(processor)
    
    # Perform RFM analysis
    rfm_data = analytics.perform_rfm_analysis()
    
    # Get customer insights
    customer_insights = analytics.get_customer_insights()
    
    # Perform ABC analysis
    product_abc, abc_stats = analytics.perform_abc_analysis()
    
    # Get seasonal patterns
    seasonal_patterns = analytics.get_seasonal_patterns()
    
    # Generate business report
    report = analytics.generate_business_report()
    
    print("\n📊 Analytics completed successfully!")
    print(f"🎯 Key insights generated for {len(rfm_data)} customers")
    print(f"📈 Seasonal patterns identified with {seasonal_patterns['seasonality_score']:.1f}% seasonality")
    print(f"📦 ABC analysis completed for inventory optimization")

if __name__ == "__main__":
    main() 