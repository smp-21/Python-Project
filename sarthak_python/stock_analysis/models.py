from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError({'date_of_birth': 'Future dates are not allowed for Date of Birth.'})
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class StockAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    ticker1 = models.CharField(max_length=10)
    ticker2 = models.CharField(max_length=10)
    analysis_date = models.DateTimeField(default=timezone.now)
    data_points = models.IntegerField()
    
    # Predictions
    ticker1_current_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticker1_predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticker2_current_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticker2_predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Model metrics
    ticker1_mae = models.DecimalField(max_digits=10, decimal_places=4)
    ticker1_mse = models.DecimalField(max_digits=10, decimal_places=4)
    ticker1_rmse = models.DecimalField(max_digits=10, decimal_places=4)
    ticker1_mape = models.DecimalField(max_digits=10, decimal_places=4)
    
    ticker2_mae = models.DecimalField(max_digits=10, decimal_places=4)
    ticker2_mse = models.DecimalField(max_digits=10, decimal_places=4)
    ticker2_rmse = models.DecimalField(max_digits=10, decimal_places=4)
    ticker2_mape = models.DecimalField(max_digits=10, decimal_places=4)
    
    class Meta:
        verbose_name_plural = "Stock Analyses"
        ordering = ['-analysis_date']
    
    def __str__(self):
        return f"{self.ticker1} vs {self.ticker2} - {self.analysis_date.strftime('%Y-%m-%d %H:%M')}" 