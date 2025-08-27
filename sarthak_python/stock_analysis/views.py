import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime, timedelta
import base64
import io
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import StockAnalysis, UserProfile

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return render(request, 'stock_analysis/home.html')
    else:
        return redirect('stock_analysis:login')

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to Stock Analyzer.')
            return redirect('stock_analysis:home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'stock_analysis/register.html', {'form': form})

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('stock_analysis:home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('stock_analysis:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()
    
    return render(request, 'stock_analysis/login.html', {'form': form})

def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('stock_analysis:login')

@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('stock_analysis:profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    
    # Get user's analysis history
    analyses = StockAnalysis.objects.filter(user=request.user).order_by('-analysis_date')[:10]
    
    return render(request, 'stock_analysis/profile.html', {
        'form': form,
        'analyses': analyses
    })

@login_required
@csrf_exempt
def analyze_stocks(request):
    """Analyze stocks and return results"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticker1 = data.get('ticker1', '').upper()
            ticker2 = data.get('ticker2', '').upper()
            
            if not ticker1 or not ticker2:
                return JsonResponse({'error': 'Please provide both ticker symbols'}, status=400)
            
            # Date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            
            # Download data
            data1 = yf.download(ticker1, start=start_date, end=end_date, auto_adjust=True)
            data2 = yf.download(ticker2, start=start_date, end=end_date, auto_adjust=True)
            
            # Check if data was downloaded successfully
            if data1.empty or data2.empty:
                return JsonResponse({'error': f'Unable to fetch data for {ticker1} or {ticker2}. Please check the ticker symbols.'}, status=400)
            
            data1 = data1['Close']
            data2 = data2['Close']
            
            # Combine the two dataframes
            data = pd.concat([data1, data2], axis=1)
            data.columns = [ticker1, ticker2]
            
            # Drop null records
            data.dropna(inplace=True)
            
            if data.shape[0] == 0:
                return JsonResponse({'error': 'No overlapping data available for the specified tickers'}, status=400)
            
            # Replace NAN values
            imputer = SimpleImputer(missing_values=np.nan, strategy='mean')
            data = pd.DataFrame(imputer.fit_transform(data), columns=data.columns)
            
            # Statistical analysis
            statistics = {
                'count': data.count().to_dict(),
                'sum': data.sum().to_dict(),
                'min': data.min().to_dict(),
                'max': data.max().to_dict(),
                'mean': data.mean().to_dict(),
                'median': data.median().to_dict(),
                'variance': data.var().to_dict(),
                'std_deviation': data.std().to_dict()
            }
            
            # Create visualizations
            charts = create_charts(data, ticker1, ticker2)
            
            # Train models and get predictions
            predictions, metrics = train_models_and_predict(data, ticker1, ticker2)
            
            # Save analysis to database
            try:
                analysis = StockAnalysis.objects.create(
                    user=request.user,
                    ticker1=ticker1,
                    ticker2=ticker2,
                    data_points=len(data),
                    ticker1_current_price=predictions[ticker1]['current_price'],
                    ticker1_predicted_price=predictions[ticker1]['predicted_price'],
                    ticker2_current_price=predictions[ticker2]['current_price'],
                    ticker2_predicted_price=predictions[ticker2]['predicted_price'],
                    ticker1_mae=metrics[ticker1]['mae'],
                    ticker1_mse=metrics[ticker1]['mse'],
                    ticker1_rmse=metrics[ticker1]['rmse'],
                    ticker1_mape=metrics[ticker1]['mape'],
                    ticker2_mae=metrics[ticker2]['mae'],
                    ticker2_mse=metrics[ticker2]['mse'],
                    ticker2_rmse=metrics[ticker2]['rmse'],
                    ticker2_mape=metrics[ticker2]['mape']
                )
            except Exception as e:
                print(f"Error saving analysis: {e}")
            
            # Prepare response
            response_data = {
                'statistics': statistics,
                'charts': charts,
                'predictions': predictions,
                'metrics': metrics,
                'data_points': len(data)
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Only POST method allowed'}, status=405)

def create_charts(data, ticker1, ticker2):
    """Create interactive charts using Plotly"""
    charts = {}
    
    # Line chart
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(x=data.index, y=data[ticker1], mode='lines', name=ticker1, line=dict(color='#667eea')))
    fig_line.add_trace(go.Scatter(x=data.index, y=data[ticker2], mode='lines', name=ticker2, line=dict(color='#764ba2')))
    fig_line.update_layout(
        title='Stock Price Comparison',
        xaxis_title='Date',
        yaxis_title='Price',
        height=400,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    charts['line_chart'] = fig_line.to_json()
    
    # Scatter plot
    fig_scatter = go.Figure()
    fig_scatter.add_trace(go.Scatter(x=data.index, y=data[ticker1], mode='markers', name=ticker1, marker=dict(color='#667eea', size=6)))
    fig_scatter.add_trace(go.Scatter(x=data.index, y=data[ticker2], mode='markers', name=ticker2, marker=dict(color='#764ba2', size=6)))
    fig_scatter.update_layout(
        title='Stock Price Scatter Plot',
        xaxis_title='Date',
        yaxis_title='Price',
        height=400,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    charts['scatter_chart'] = fig_scatter.to_json()
    
    # Histogram
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(x=data[ticker1], name=ticker1, opacity=0.7, marker_color='#667eea'))
    fig_hist.add_trace(go.Histogram(x=data[ticker2], name=ticker2, opacity=0.7, marker_color='#764ba2'))
    fig_hist.update_layout(
        title='Price Distribution',
        xaxis_title='Price',
        yaxis_title='Frequency',
        height=400,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50),
        barmode='overlay'
    )
    charts['histogram'] = fig_hist.to_json()
    
    # Correlation heatmap
    correlation_matrix = data.corr()
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(correlation_matrix.values, 3),
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    fig_heatmap.update_layout(
        title='Correlation Matrix',
        height=400,
        template='plotly_white',
        margin=dict(l=50, r=50, t=50, b=50)
    )
    charts['correlation_heatmap'] = fig_heatmap.to_json()
    
    return charts

def train_models_and_predict(data, ticker1, ticker2):
    """Train KNN models and make predictions"""
    # Prepare data for modeling
    X1 = data[[ticker2]]  # Use ticker2 to predict ticker1
    y1 = data[ticker1]
    
    X2 = data[[ticker1]]  # Use ticker1 to predict ticker2
    y2 = data[ticker2]
    
    # Scale the data
    scaler1 = StandardScaler()
    X1_scaled = scaler1.fit_transform(X1)
    
    scaler2 = StandardScaler()
    X2_scaled = scaler2.fit_transform(X2)
    
    # Train models
    k = 5
    knn_regressor1 = KNeighborsRegressor(n_neighbors=k)
    knn_regressor1.fit(X1_scaled, y1)
    
    knn_regressor2 = KNeighborsRegressor(n_neighbors=k)
    knn_regressor2.fit(X2_scaled, y2)
    
    # Make predictions for next day
    last_data_point = data.iloc[[-1]]
    
    # Predict next day's closing price for ticker1
    X1_next_day = last_data_point[[ticker2]]
    X1_next_day_scaled = scaler1.transform(X1_next_day)
    next_day_price1 = knn_regressor1.predict(X1_next_day_scaled)[0]
    
    # Predict next day's closing price for ticker2
    X2_next_day = last_data_point[[ticker1]]
    X2_next_day_scaled = scaler2.transform(X2_next_day)
    next_day_price2 = knn_regressor2.predict(X2_next_day_scaled)[0]
    
    # Calculate metrics
    mae1 = mean_absolute_error(y1, knn_regressor1.predict(X1_scaled))
    mse1 = mean_squared_error(y1, knn_regressor1.predict(X1_scaled))
    rmse1 = np.sqrt(mse1)
    mape1 = np.mean(np.abs((y1 - knn_regressor1.predict(X1_scaled)) / y1)) * 100
    
    mae2 = mean_absolute_error(y2, knn_regressor2.predict(X2_scaled))
    mse2 = mean_squared_error(y2, knn_regressor2.predict(X2_scaled))
    rmse2 = np.sqrt(mse2)
    mape2 = np.mean(np.abs((y2 - knn_regressor2.predict(X2_scaled)) / y2)) * 100
    
    predictions = {
        ticker1: {
            'current_price': float(data[ticker1].iloc[-1]),
            'predicted_price': float(next_day_price1)
        },
        ticker2: {
            'current_price': float(data[ticker2].iloc[-1]),
            'predicted_price': float(next_day_price2)
        }
    }
    
    metrics = {
        ticker1: {
            'mae': float(mae1),
            'mse': float(mse1),
            'rmse': float(rmse1),
            'mape': float(mape1)
        },
        ticker2: {
            'mae': float(mae2),
            'mse': float(mse2),
            'rmse': float(rmse2),
            'mape': float(mape2)
        }
    }
    
    return predictions, metrics 