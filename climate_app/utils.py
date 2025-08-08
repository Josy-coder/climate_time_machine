import requests
from datetime import datetime, timedelta
from typing import Dict, List
import statistics

class OpenMeteoAPI:
    """Utility class for Open-Meteo API interactions"""

    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"

    @staticmethod
    def search_locations(query: str) -> List[Dict]:
        """Search for locations using Open-Meteo Geocoding API"""
        try:
            response = requests.get(
                OpenMeteoAPI.GEOCODING_URL,
                params={
                    'name': query,
                    'count': 5,
                    'language': 'en',
                    'format': 'json'
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            locations = []
            if 'results' in data:
                for result in data['results']:
                    locations.append({
                        'name': result.get('name', ''),
                        'country': result.get('country', ''),
                        'latitude': result.get('latitude'),
                        'longitude': result.get('longitude'),
                        'display_name': f"{result.get('name', '')}, {result.get('country', '')}"
                    })

            return locations
        except Exception as e:
            print(f"Error searching locations: {e}")
            return []

    @staticmethod
    def get_historical_data(lat: float, lng: float, start_year: int, end_year: int) -> Dict:
        """Get historical weather data for a decade"""
        try:
            response = requests.get(
                OpenMeteoAPI.HISTORICAL_URL,
                params={
                    'latitude': lat,
                    'longitude': lng,
                    'start_date': f'{start_year}-01-01',
                    'end_date': f'{end_year}-12-31',
                    'daily': 'temperature_2m_max,temperature_2m_min,temperature_2m_mean',
                    'timezone': 'auto'
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return {}

class ClimateAnalyzer:
    """Analyze climate data"""

    @staticmethod
    def calculate_temperature_stats(daily_data: Dict) -> Dict:
        """Calculate temperature statistics from daily data"""
        if not daily_data or 'daily' not in daily_data:
            return {}

        daily = daily_data['daily']
        max_temps = [t for t in daily.get('temperature_2m_max', []) if t is not None]
        min_temps = [t for t in daily.get('temperature_2m_min', []) if t is not None]
        mean_temps = [t for t in daily.get('temperature_2m_mean', []) if t is not None]

        if not max_temps:
            return {}

        return {
            'avg_max_temp': round(statistics.mean(max_temps), 1),
            'avg_min_temp': round(statistics.mean(min_temps), 1) if min_temps else 0,
            'avg_mean_temp': round(statistics.mean(mean_temps), 1) if mean_temps else 0,
            'hottest_day': round(max(max_temps), 1),
            'extreme_hot_days': len([t for t in max_temps if t > 30]),
            'total_days': len(max_temps)
        }