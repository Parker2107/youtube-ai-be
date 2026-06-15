from django.urls import path
from . import views

urlpatterns = [
    # path('your-endpoint/', views.your_view_function, name='your-endpoint'),
    path('health/', views.health_check, name='health-check')
]