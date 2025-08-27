from django.contrib import admin
from .models import StockAnalysis, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(StockAnalysis)
class StockAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker1', 'ticker2', 'analysis_date', 'data_points')
    list_filter = ('analysis_date', 'ticker1', 'ticker2', 'user')
    search_fields = ('ticker1', 'ticker2', 'user__username')
    readonly_fields = ('analysis_date',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Stock Information', {
            'fields': ('ticker1', 'ticker2', 'analysis_date', 'data_points')
        }),
        ('Predictions', {
            'fields': (
                'ticker1_current_price', 'ticker1_predicted_price',
                'ticker2_current_price', 'ticker2_predicted_price'
            )
        }),
        ('Model Metrics - Ticker 1', {
            'fields': ('ticker1_mae', 'ticker1_mse', 'ticker1_rmse', 'ticker1_mape')
        }),
        ('Model Metrics - Ticker 2', {
            'fields': ('ticker2_mae', 'ticker2_mse', 'ticker2_rmse', 'ticker2_mape')
        }),
    ) 