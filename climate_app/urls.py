from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.LocationSearchView.as_view(), name='location_search'),
    # Better solution: Use query parameters
    path('compare/', views.ClimateComparisonView.as_view(), name='climate_comparison'),
    path('test-api/', views.TestAPIView.as_view(), name='test_api'),
]