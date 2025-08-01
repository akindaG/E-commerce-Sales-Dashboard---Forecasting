"""
Forecasting Module for E-commerce Analytics
Handles revenue forecasting using time series analysis and ML models
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objects as go
import plotly.express as px

class RevenueForecaster:
    def __init__(self, data_processor=None):
        """
        Initialize the revenue forecaster
        
        Args:
            data_processor: EcommerceDataProcessor instance with cleaned data
        """
        self.data_processor = data_processor
        self.monthly_data = None
        self.forecast_results = {}
        
    def prepare_time_series_data(self):
        """Prepare monthly time series data for forecasting"""
        if self.data_processor is None or self.data_processor.cleaned_df is None:
            print("[ERROR] No data available. Please provide data processor with cleaned data.")
            return None
            
        df = self.data_processor.cleaned_df
        
        # Aggregate by month
        monthly_data = df.groupby(df['InvoiceDate'].dt.to_period('M')).agg({
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        monthly_data.columns = ['Month', 'Revenue', 'Orders', 'Customers', 'Quantity']
        monthly_data['Month'] = monthly_data['Month'].dt.to_timestamp()
        monthly_data['Avg_Order_Value'] = monthly_data['Revenue'] / monthly_data['Orders']
        
        # Add time features
        monthly_data['Month_Num'] = range(len(monthly_data))
        monthly_data['Year'] = monthly_data['Month'].dt.year
        monthly_data['Month_Of_Year'] = monthly_data['Month'].dt.month
        
        self.monthly_data = monthly_data
        
        print(f"[OK] Time series data prepared: {len(monthly_data)} months")
        return monthly_data
    
    def perform_seasonal_decomposition(self):
        """Perform seasonal decomposition of the time series"""
        if self.monthly_data is None:
            print("[ERROR] No monthly data available. Please prepare time series data first.")
            return None
            
        # Check if we have enough data for seasonal decomposition
        if len(self.monthly_data) < 24:
            print("⚠️  Insufficient data for seasonal decomposition (need at least 24 months)")
            print("   Using trend-only decomposition instead")
            # Use a simpler approach for limited data
            decomposition_results = {
                'trend': self.monthly_data['Revenue'].rolling(window=3, center=True).mean(),
                'seasonal': pd.Series(0, index=self.monthly_data.index),  # No seasonality
                'residual': self.monthly_data['Revenue'] - self.monthly_data['Revenue'].rolling(window=3, center=True).mean(),
                'observed': self.monthly_data['Revenue']
            }
            return decomposition_results
            
        # Perform seasonal decomposition
        decomposition = seasonal_decompose(
            self.monthly_data['Revenue'], 
            model='additive', 
            period=12  # Assuming 12-month seasonality
        )
        
        decomposition_results = {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'observed': decomposition.observed
        }
        
        return decomposition_results
    
    def simple_linear_forecast(self, periods=6):
        """Simple linear regression forecast"""
        if self.monthly_data is None:
            print("[ERROR] No monthly data available. Please prepare time series data first.")
            return None
            
        X = self.monthly_data['Month_Num'].values.reshape(-1, 1)
        y = self.monthly_data['Revenue'].values
        
        # Fit linear model
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate future periods
        future_X = np.arange(len(X), len(X) + periods).reshape(-1, 1)
        forecast = model.predict(future_X)
        
        # Calculate confidence intervals (simple approach)
        residuals = y - model.predict(X)
        std_residuals = np.std(residuals)
        confidence_interval = 1.96 * std_residuals  # 95% confidence
        
        results = {
            'forecast': forecast,
            'confidence_upper': forecast + confidence_interval,
            'confidence_lower': forecast - confidence_interval,
            'model': model,
            'r2_score': model.score(X, y),
            'mae': mean_absolute_error(y, model.predict(X))
        }
        
        self.forecast_results['linear'] = results
        return results
    
    def polynomial_forecast(self, degree=2, periods=6):
        """Polynomial regression forecast"""
        if self.monthly_data is None:
            print("[ERROR] No monthly data available. Please prepare time series data first.")
            return None
            
        X = self.monthly_data['Month_Num'].values.reshape(-1, 1)
        y = self.monthly_data['Revenue'].values
        
        # Create polynomial features
        poly_features = PolynomialFeatures(degree=degree)
        X_poly = poly_features.fit_transform(X)
        
        # Fit polynomial model
        model = LinearRegression()
        model.fit(X_poly, y)
        
        # Generate future periods
        future_X = np.arange(len(X), len(X) + periods).reshape(-1, 1)
        future_X_poly = poly_features.transform(future_X)
        forecast = model.predict(future_X_poly)
        
        # Calculate confidence intervals
        residuals = y - model.predict(X_poly)
        std_residuals = np.std(residuals)
        confidence_interval = 1.96 * std_residuals
        
        results = {
            'forecast': forecast,
            'confidence_upper': forecast + confidence_interval,
            'confidence_lower': forecast - confidence_interval,
            'model': model,
            'poly_features': poly_features,
            'r2_score': model.score(X_poly, y),
            'mae': mean_absolute_error(y, model.predict(X_poly))
        }
        
        self.forecast_results['polynomial'] = results
        return results
    
    def seasonal_forecast(self, periods=6):
        """Forecast with seasonal patterns"""
        if self.monthly_data is None:
            print("[ERROR] No monthly data available. Please prepare time series data first.")
            return None
            
        # Check if we have enough data for seasonal analysis
        if len(self.monthly_data) < 24:
            print("[INFO] Insufficient data for seasonal forecasting, using polynomial forecast instead")
            return self.polynomial_forecast(periods=periods)
            
        # Get seasonal decomposition
        decomposition = self.perform_seasonal_decomposition()
        if decomposition is None:
            return None
        
        # Extract seasonal pattern
        seasonal_pattern = decomposition['seasonal'].dropna()
        
        # If we have enough data, use the seasonal pattern
        if len(seasonal_pattern) >= 12:
            # Use the last 12 months of seasonal pattern
            last_seasonal = seasonal_pattern.tail(12).values
            
            # Extend trend using linear regression
            trend_data = decomposition['trend'].dropna()
            if len(trend_data) > 1:
                X_trend = np.arange(len(trend_data)).reshape(-1, 1)
                y_trend = trend_data.values
                
                trend_model = LinearRegression()
                trend_model.fit(X_trend, y_trend)
                
                # Forecast trend
                future_trend_X = np.arange(len(trend_data), len(trend_data) + periods).reshape(-1, 1)
                trend_forecast = trend_model.predict(future_trend_X)
                
                # Combine trend and seasonal
                forecast = trend_forecast + last_seasonal[:periods]
                
                results = {
                    'forecast': forecast,
                    'trend_forecast': trend_forecast,
                    'seasonal_pattern': last_seasonal,
                    'model': trend_model,
                    'r2_score': trend_model.score(X_trend, y_trend)
                }
                
                self.forecast_results['seasonal'] = results
                return results
        
        # Fallback to polynomial forecast
        return self.polynomial_forecast(periods=periods)
    
    def ensemble_forecast(self, periods=6):
        """Combine multiple forecasting methods"""
        if self.monthly_data is None:
            print("[ERROR] No monthly data available. Please prepare time series data first.")
            return None
        
        # Run different forecasting methods
        linear_results = self.simple_linear_forecast(periods)
        poly_results = self.polynomial_forecast(periods)
        seasonal_results = self.seasonal_forecast(periods)
        
        # Handle cases where some methods fail
        available_forecasts = []
        forecast_names = []
        
        if linear_results:
            available_forecasts.append(linear_results['forecast'])
            forecast_names.append('linear')
        if poly_results:
            available_forecasts.append(poly_results['forecast'])
            forecast_names.append('polynomial')
        if seasonal_results:
            available_forecasts.append(seasonal_results['forecast'])
            forecast_names.append('seasonal')
        
        if len(available_forecasts) >= 2:
            # Ensure all forecasts have the same length
            min_length = min(len(f) for f in available_forecasts)
            if min_length != periods:
                print(f"[WARNING] Truncating forecasts to {min_length} periods (requested {periods})")
            
            # Truncate all forecasts to the minimum length
            truncated_forecasts = [f[:min_length] for f in available_forecasts]
            
            # Combine available forecasts (simple average)
            ensemble_forecast = np.mean(truncated_forecasts, axis=0)
            
            # Calculate ensemble confidence intervals
            forecasts = np.column_stack(truncated_forecasts)
            forecast_std = np.std(forecasts, axis=1)
            confidence_interval = 1.96 * forecast_std
            
            # Create individual forecasts dict with truncated values
            individual_forecasts = {}
            if linear_results:
                individual_forecasts['linear'] = linear_results['forecast'][:min_length]
            if poly_results:
                individual_forecasts['polynomial'] = poly_results['forecast'][:min_length]
            if seasonal_results:
                individual_forecasts['seasonal'] = seasonal_results['forecast'][:min_length]
            
            results = {
                'forecast': ensemble_forecast,
                'confidence_upper': ensemble_forecast + confidence_interval,
                'confidence_lower': ensemble_forecast - confidence_interval,
                'individual_forecasts': individual_forecasts,
                'forecast_std': forecast_std,
                'methods_used': forecast_names
            }
            
            self.forecast_results['ensemble'] = results
            return results
        elif len(available_forecasts) == 1:
            # Use the single available forecast
            single_forecast = available_forecasts[0]
            forecast_name = forecast_names[0]
            
            results = {
                'forecast': single_forecast,
                'confidence_upper': single_forecast * 1.1,  # Simple confidence interval
                'confidence_lower': single_forecast * 0.9,
                'individual_forecasts': {forecast_name: single_forecast},
                'methods_used': [forecast_name]
            }
            
            self.forecast_results['ensemble'] = results
            return results
        
        print("[ERROR] No forecasting methods could be executed successfully")
        return None
    
    def generate_forecast_dates(self, periods=6):
        """Generate future dates for the forecast"""
        if self.monthly_data is None:
            return None
            
        last_date = self.monthly_data['Month'].max()
        future_dates = []
        
        for i in range(1, periods + 1):
            future_date = last_date + pd.DateOffset(months=i)
            future_dates.append(future_date)
        
        return future_dates
    
    def create_forecast_visualization(self, forecast_type='ensemble', periods=6):
        """Create interactive forecast visualization"""
        if forecast_type not in self.forecast_results:
            print(f"[ERROR] Forecast type '{forecast_type}' not available.")
            return None
        
        forecast_data = self.forecast_results[forecast_type]
        future_dates = self.generate_forecast_dates(periods)
        
        if future_dates is None:
            return None
        
        # Create the plot
        fig = go.Figure()
        
        # Historical data
        fig.add_trace(go.Scatter(
            x=self.monthly_data['Month'],
            y=self.monthly_data['Revenue'],
            mode='lines+markers',
            name='Historical Revenue',
            line=dict(color='blue', width=2),
            marker=dict(size=6)
        ))
        
        # Forecast
        fig.add_trace(go.Scatter(
            x=future_dates,
            y=forecast_data['forecast'],
            mode='lines+markers',
            name='Forecast',
            line=dict(color='red', width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        # Confidence intervals if available
        if 'confidence_upper' in forecast_data and 'confidence_lower' in forecast_data:
            fig.add_trace(go.Scatter(
                x=future_dates + future_dates[::-1],
                y=np.concatenate([forecast_data['confidence_upper'], forecast_data['confidence_lower'][::-1]]),
                fill='toself',
                fillcolor='rgba(255,0,0,0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='95% Confidence Interval',
                showlegend=True
            ))
        
        # Update layout
        fig.update_layout(
            title=f'Revenue Forecast - {forecast_type.title()} Model',
            xaxis_title='Date',
            yaxis_title='Revenue ($)',
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig
    
    def get_forecast_summary(self, forecast_type='ensemble'):
        """Get summary statistics for the forecast"""
        if forecast_type not in self.forecast_results:
            print(f"[ERROR] Forecast type '{forecast_type}' not available.")
            return None
        
        forecast_data = self.forecast_results[forecast_type]
        
        summary = {
            'forecast_type': forecast_type,
            'forecast_periods': len(forecast_data['forecast']),
            'total_forecasted_revenue': np.sum(forecast_data['forecast']),
            'avg_monthly_forecast': np.mean(forecast_data['forecast']),
            'forecast_growth_rate': self._calculate_growth_rate(forecast_data['forecast']),
            'model_performance': {}
        }
        
        # Add model performance metrics if available
        if 'r2_score' in forecast_data:
            summary['model_performance']['r2_score'] = forecast_data['r2_score']
        if 'mae' in forecast_data:
            summary['model_performance']['mae'] = forecast_data['mae']
        
        return summary
    
    def _calculate_growth_rate(self, forecast_values):
        """Calculate growth rate from forecast values"""
        if len(forecast_values) < 2:
            return 0
        
        first_value = forecast_values[0]
        last_value = forecast_values[-1]
        
        if first_value == 0:
            return 0
        
        growth_rate = ((last_value - first_value) / first_value) * 100
        return growth_rate
    
    def generate_forecast_report(self, periods=6):
        """Generate comprehensive forecast report"""
        if self.monthly_data is None:
            print("[ERROR] No monthly data available. Please prepare time series data first.")
            return None
        
        # Run all forecasting methods
        self.ensemble_forecast(periods)
        
        # Get forecast summary
        summary = self.get_forecast_summary('ensemble')
        
        # Generate visualizations
        fig = self.create_forecast_visualization('ensemble', periods)
        
        # Create report
        report = {
            'summary': summary,
            'visualization': fig,
            'forecast_data': self.forecast_results,
            'historical_data': self.monthly_data,
            'recommendations': self._generate_forecast_recommendations(summary)
        }
        
        return report
    
    def _generate_forecast_recommendations(self, summary):
        """Generate recommendations based on forecast results"""
        recommendations = []
        
        if summary:
            growth_rate = summary['forecast_growth_rate']
            avg_forecast = summary['avg_monthly_forecast']
            
            if growth_rate > 10:
                recommendations.append({
                    'type': 'Positive',
                    'message': f'Strong growth forecasted ({growth_rate:.1f}%) - consider expanding inventory and marketing',
                    'priority': 'High'
                })
            elif growth_rate > 0:
                recommendations.append({
                    'type': 'Positive',
                    'message': f'Moderate growth forecasted ({growth_rate:.1f}%) - maintain current strategies',
                    'priority': 'Medium'
                })
            else:
                recommendations.append({
                    'type': 'Warning',
                    'message': f'Declining trend forecasted ({growth_rate:.1f}%) - review business strategies',
                    'priority': 'High'
                })
            
            # Add seasonal recommendations
            if hasattr(self, 'monthly_data') and self.monthly_data is not None:
                seasonal_decomp = self.perform_seasonal_decomposition()
                if seasonal_decomp and 'seasonal' in seasonal_decomp:
                    seasonal_strength = np.std(seasonal_decomp['seasonal'].dropna())
                    if seasonal_strength > 10000:  # Threshold for strong seasonality
                        recommendations.append({
                            'type': 'Info',
                            'message': 'Strong seasonal patterns detected - plan inventory accordingly',
                            'priority': 'Medium'
                        })
        
        return recommendations

def main():
    """Main function to demonstrate forecasting capabilities"""
    from data_processing import EcommerceDataProcessor
    
    # Initialize data processor
    processor = EcommerceDataProcessor()
    
    # Load and clean data
    processor.load_data()
    processor.clean_data()
    
    # Initialize forecaster
    forecaster = RevenueForecaster(processor)
    
    # Prepare time series data
    monthly_data = forecaster.prepare_time_series_data()
    
    # Generate forecast report
    report = forecaster.generate_forecast_report(periods=6)
    
    if report:
        print("\n📈 Forecasting completed successfully!")
        print(f"💰 Total forecasted revenue: ${report['summary']['total_forecasted_revenue']:,.2f}")
        print(f"📊 Growth rate: {report['summary']['forecast_growth_rate']:.1f}%")
        print(f"🎯 Average monthly forecast: ${report['summary']['avg_monthly_forecast']:,.2f}")
        
        # Display recommendations
        print("\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec['message']}")

if __name__ == "__main__":
    main() 