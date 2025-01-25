from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('calculate_score/', views.calculate_score, name='calculate_score'),
    path('get_all_scores/', views.get_all_scores, name='get_all_scores'),
]
