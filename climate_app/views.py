from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .utils import OpenMeteoAPI, ClimateAnalyzer
import json

class HomeView(View):
    def get(self, request):
        return render(request, 'index.html')

class LocationSearchView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()

        if len(query) < 2:
            return render(request, 'partials/location_suggestions.html', {
                'locations': []
            })

        locations = OpenMeteoAPI.search_locations(query)

        return render(request, 'partials/location_suggestions.html', {
            'locations': locations
        })

class ClimateComparisonView(View):
    def get(self, request):
        print(f"DEBUG: ClimateComparisonView called with params: {request.GET}")
        print(f"DEBUG: Is HTMX request: {hasattr(request, 'htmx') and request.htmx}")

        # Get coordinates from query parameters instead of URL path
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        location_name = request.GET.get('name', 'Selected Location')

        print(f"DEBUG: lat={lat}, lng={lng}, name={location_name}")

        if not lat or not lng:
            error_msg = f"<div class='bg-red-100 p-4 rounded'>Missing coordinates. Got lat={lat}, lng={lng}</div>"
            print(f"DEBUG: Returning error: {error_msg}")
            return HttpResponse(error_msg)

        print(f"DEBUG: Fetching data for {location_name} at {lat}, {lng}")

        try:
            # Get 1970s data
            print("DEBUG: Fetching historical data...")
            historical_data = OpenMeteoAPI.get_historical_data(
                float(lat), float(lng), 1970, 1979
            )
            print(f"DEBUG: Historical data keys: {historical_data.keys() if historical_data else 'None'}")

            # Get recent data (2020-2024)
            print("DEBUG: Fetching recent data...")
            recent_data = OpenMeteoAPI.get_historical_data(
                float(lat), float(lng), 2020, 2024
            )
            print(f"DEBUG: Recent data keys: {recent_data.keys() if recent_data else 'None'}")

            # Analyze data
            historical_stats = ClimateAnalyzer.calculate_temperature_stats(historical_data)
            recent_stats = ClimateAnalyzer.calculate_temperature_stats(recent_data)

            print(f"DEBUG: Historical stats: {historical_stats}")
            print(f"DEBUG: Recent stats: {recent_stats}")

            # Calculate change
            temperature_change = 0
            if historical_stats and recent_stats:
                temperature_change = recent_stats['avg_mean_temp'] - historical_stats['avg_mean_temp']

            context = {
                'location_name': location_name,
                'historical_stats': historical_stats,
                'recent_stats': recent_stats,
                'temperature_change': round(temperature_change, 1),
                'has_data': bool(historical_stats and recent_stats),
                'debug_info': f"Hist: {bool(historical_data)}, Recent: {bool(recent_data)}"
            }

            template = 'partials/comparison_dashboard.html' if request.htmx else 'comparison.html'
            return render(request, template, context)

        except Exception as e:
            print(f"DEBUG: Error in comparison view: {e}")
            return HttpResponse(f"<div class='bg-red-100 p-4 rounded'>Error: {str(e)}</div>")

class TestAPIView(View):
    def get(self, request):
        # Test the API with a known location (London)
        try:
            locations = OpenMeteoAPI.search_locations("London")
            historical_data = OpenMeteoAPI.get_historical_data(51.5074, -0.1278, 1970, 1971)

            return HttpResponse(f"""
            <div class="bg-white p-4 rounded shadow">
                <h3>API Test Results:</h3>
                <p><strong>Locations found:</strong> {len(locations)}</p>
                <p><strong>Historical data keys:</strong> {list(historical_data.keys()) if historical_data else 'None'}</p>
                <pre style="font-size: 12px; background: #f5f5f5; padding: 10px; overflow: auto;">
                {json.dumps(historical_data, indent=2) if historical_data else 'No data'}
                </pre>
            </div>
            """)
        except Exception as e:
            return HttpResponse(f"<div class='bg-red-100 p-4'>API Test Error: {str(e)}</div>")