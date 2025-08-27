# Stock Analyzer - Django Web Application

A modern Django web application for analyzing and comparing stock performance using machine learning predictions.

## Features

- **Interactive Stock Analysis**: Compare two stocks with real-time data from Yahoo Finance
- **Machine Learning Predictions**: K-Nearest Neighbors (KNN) algorithm for price predictions
- **Beautiful Visualizations**: Interactive charts using Plotly
- **Statistical Analysis**: Comprehensive statistics and metrics
- **Modern UI**: Responsive design with Bootstrap 5
- **Model Performance Metrics**: MAE, MSE, RMSE, and MAPE calculations

## Technologies Used

- **Backend**: Django 4.2.7
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **Stock Data**: yfinance
- **Visualizations**: Plotly
- **Frontend**: Bootstrap 5, Font Awesome
- **Machine Learning**: K-Nearest Neighbors Regressor

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd stock-analyzer
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (optional)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Open your browser** and navigate to `http://127.0.0.1:8000/`

## Usage

1. **Enter Stock Tickers**: Input two stock ticker symbols (e.g., AAPL, GOOGL, MSFT)
2. **Click Analyze**: The application will fetch real-time data and perform analysis
3. **View Results**: 
   - Current and predicted prices
   - Statistical analysis
   - Interactive charts
   - Model performance metrics

## Features Explained

### Stock Analysis
- Fetches 90 days of historical data from Yahoo Finance
- Handles missing data with imputation
- Performs comprehensive statistical analysis

### Machine Learning
- Uses K-Nearest Neighbors (KNN) algorithm
- Standardizes data for better predictions
- Calculates multiple performance metrics

### Visualizations
- **Line Chart**: Stock price comparison over time
- **Scatter Plot**: Price distribution analysis
- **Histogram**: Price frequency distribution
- **Correlation Heatmap**: Relationship between stocks

### Model Metrics
- **MAE (Mean Absolute Error)**: Average absolute difference between predicted and actual values
- **MSE (Mean Squared Error)**: Average squared difference
- **RMSE (Root Mean Squared Error)**: Square root of MSE
- **MAPE (Mean Absolute Percentage Error)**: Average percentage error

## Project Structure

```
stock_analyzer/
├── manage.py
├── requirements.txt
├── README.md
├── stock_analyzer/          # Main Django project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── stock_analysis/          # Django app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── templates/
│   └── stock_analysis/
│       └── home.html
└── static/                  # Static files (CSS, JS)
```

## API Endpoints

- `GET /`: Home page with analysis form
- `POST /analyze/`: Analyze stocks and return JSON results

## Admin Interface

Access the Django admin interface at `http://127.0.0.1:8000/admin/` to:
- View analysis history
- Monitor model performance
- Manage stock analysis records

## Customization

### Adding New Features
1. **New Analysis Methods**: Add functions in `views.py`
2. **Additional Charts**: Extend the `create_charts()` function
3. **Different ML Models**: Modify `train_models_and_predict()`

### Styling
- Modify CSS in `templates/stock_analysis/home.html`
- Add custom Bootstrap classes
- Update color scheme in CSS variables

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**: Run migrations
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Stock Data Issues**: Check internet connection and ticker symbols

4. **Chart Display Issues**: Ensure JavaScript is enabled in browser

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Acknowledgments

- Yahoo Finance for stock data
- Django community for the excellent framework
- Plotly for interactive visualizations
- Bootstrap for responsive design 