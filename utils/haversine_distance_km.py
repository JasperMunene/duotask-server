import math

def haversine_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculates the Haversine distance between two latitude/longitude pairs in kilometers.
    Args:
        lat1, lon1: Latitude and Longitude of point 1 (in decimal degrees)
        lat2, lon2: Latitude and Longitude of point 2 (in decimal degrees)
    Returns:
        Distance in kilometers as a float
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Radius of Earth in KM
    R = 6371.0

    # Difference in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine implementation
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c
