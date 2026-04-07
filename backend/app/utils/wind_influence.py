"""
Wind-based station influence calculator.
Determines which stations influence a target station based on wind direction.
"""

import logging
import math
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class WindInfluenceCalculator:
    """Calculate station influence based on wind direction."""
    
    # Delhi station coordinates
    STATIONS = {
        "Alipur": {"lat": 28.7986, "lon": 77.1331},
        "Bawana": {"lat": 28.623, "lon": 77.21},
        "Burari": {"lat": 28.7167, "lon": 77.2},
        "DRKARNISINGH": {"lat": 28.498571, "lon": 77.26484},
        "DTU": {"lat": 28.750049, "lon": 77.111261},
        "DWARKASEC8": {"lat": 28.571027, "lon": 77.0719},
        "IGIT3": {"lat": 28.562776, "lon": 77.118005},
        "ITO": {"lat": 28.6286, "lon": 77.241},
        "Mundka": {"lat": 28.68, "lon": 77.08},
        "Najfgarh": {"lat": 28.570173, "lon": 76.933762},
        "NARELA": {"lat": 28.822836, "lon": 77.101981},
        "Northcampus": {"lat": 28.686, "lon": 77.209},
        "NSUT": {"lat": 28.686, "lon": 77.209},
        "Punjabi_bagh": {"lat": 28.674045, "lon": 77.131023},
        "RKPuram": {"lat": 28.563262, "lon": 77.186937},
        "Shadipur": {"lat": 28.651, "lon": 77.146},
        "Wazirpur": {"lat": 28.699793, "lon": 77.165453},
    }
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two coordinates in km.
        """
        R = 6371  # Earth radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    @staticmethod
    def bearing_between_points(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate bearing from point 1 to point 2 in degrees (0-360).
        0° = North, 90° = East, 180° = South, 270° = West
        """
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lon = math.radians(lon2 - lon1)
        
        x = math.sin(delta_lon) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lon)
        
        bearing = math.degrees(math.atan2(x, y))
        return (bearing + 360) % 360
    
    @staticmethod
    def angle_difference(angle1: float, angle2: float) -> float:
        """Calculate minimum angle difference in degrees (0-180)."""
        diff = abs(angle1 - angle2)
        if diff > 180:
            diff = 360 - diff
        return diff
    
    @staticmethod
    def get_upwind_stations(
        target_station: str,
        wind_direction: float,
        max_distance_km: float = 15.0,
        max_angle_diff: float = 90.0,
        top_n: int = 3
    ) -> List[Dict]:
        """
        Get stations that are upwind of the target station.
        Wind carries pollution from upwind to target.
        
        Args:
            target_station: Target station name
            wind_direction: Wind direction in degrees (direction wind comes FROM)
            max_distance_km: Maximum distance to consider (default 15 km)
            max_angle_diff: Maximum angle difference from wind direction (default 90°)
            top_n: Return top N stations by influence
            
        Returns:
            List of upwind stations sorted by influence score
            [
                {
                    "station": "Shadipur",
                    "bearing": 125.0,
                    "distance": 5.5,
                    "angle_diff": 45.0,
                    "influence_score": 0.85,
                    "lat": 28.651,
                    "lon": 77.146
                },
                ...
            ]
        """
        try:
            if target_station not in WindInfluenceCalculator.STATIONS:
                logger.warning(f"Target station {target_station} not found")
                return []
            
            target = WindInfluenceCalculator.STATIONS[target_station]
            target_lat = target["lat"]
            target_lon = target["lon"]
            
            # Wind FROM 180° means wind comes from south, blows north
            # So particles move from south TO north
            # We want stations to the SOUTH of target (bearing ~180 from target)
            # that are IN the wind direction
            
            upwind_stations = []
            
            for station_name, coords in WindInfluenceCalculator.STATIONS.items():
                if station_name == target_station:
                    continue
                
                station_lat = coords["lat"]
                station_lon = coords["lon"]
                
                # Calculate distance
                distance = WindInfluenceCalculator.haversine_distance(
                    target_lat, target_lon, station_lat, station_lon
                )
                
                if distance > max_distance_km:
                    continue
                
                # Calculate bearing from target to this station
                bearing = WindInfluenceCalculator.bearing_between_points(
                    target_lat, target_lon, station_lat, station_lon
                )
                
                # Wind direction tells us where wind comes FROM
                # If wind_direction = 180°, wind comes from south
                # Particles travel FROM south TO north
                # So we want stations to the south (bearing ~180 from target)
                
                # Calculate angle difference between bearing and wind direction
                # If they're aligned, this station is upwind
                angle_diff = WindInfluenceCalculator.angle_difference(bearing, wind_direction)
                
                # Only consider stations roughly in wind direction (±max_angle_diff)
                if angle_diff > max_angle_diff:
                    continue
                
                # Calculate influence score
                # Higher score = more influence
                # Based on: closeness + alignment with wind direction
                distance_factor = 1.0 - (distance / max_distance_km)  # Close stations score higher
                angle_factor = 1.0 - (angle_diff / max_angle_diff)    # Aligned stations score higher
                influence_score = 0.6 * distance_factor + 0.4 * angle_factor
                
                upwind_stations.append({
                    "station": station_name,
                    "bearing": bearing,
                    "distance": distance,
                    "angle_diff": angle_diff,
                    "influence_score": influence_score,
                    "lat": station_lat,
                    "lon": station_lon
                })
            
            # Sort by influence score and return top N
            upwind_stations.sort(key=lambda x: x["influence_score"], reverse=True)
            
            logger.info(
                f"Upwind stations for {target_station} (wind {wind_direction}°): "
                f"{[s['station'] for s in upwind_stations[:top_n]]}"
            )
            
            return upwind_stations[:top_n]
            
        except Exception as e:
            logger.error(f"Error calculating upwind stations: {e}")
            return []
    
    @staticmethod
    def get_wind_sector(wind_direction: float) -> str:
        """
        Convert wind direction to cardinal direction.
        
        Args:
            wind_direction: Direction in degrees (0-360)
            
        Returns:
            Cardinal direction (N, NE, E, SE, S, SW, W, NW)
        """
        sectors = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                   "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
        index = int((wind_direction + 11.25) / 22.5) % 16
        return sectors[index]
