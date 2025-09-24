import random

def estimate_zone_count(area_sq_km, avg_zone_size):
    return max(1, round(area_sq_km / avg_zone_size))

def assign_traffic_level():
    return random.choice(["low", "moderate", "high"])

def generate_zones(num_zones):
    zones = {}
    for i in range(1, num_zones + 1):
        zone_id = f"Zone_{i}"
        zones[zone_id] = {
            "traffic_level": assign_traffic_level(),
            "num_customers": random.randint(50, 200)
            # Removed num_riders - will be calculated based on city total
        }
    return zones

def distribute_riders_across_zones(total_riders, num_zones):
    """Distribute total riders across zones, ensuring each zone gets at least 1 rider"""
    if total_riders < num_zones:
        raise ValueError(f"Total riders ({total_riders}) must be at least equal to number of zones ({num_zones})")
    
    # Give at least 1 rider to each zone
    riders_per_zone = [1] * num_zones
    remaining_riders = total_riders - num_zones
    
    # Distribute remaining riders randomly
    for _ in range(remaining_riders):
        zone_index = random.randint(0, num_zones - 1)
        riders_per_zone[zone_index] += 1
    
    return riders_per_zone

def get_traffic_factor(traffic_level, day_type, time_slot):
    """Calculate traffic factor based on conditions"""
    base_factors = {"low": 1.0, "moderate": 1.2, "high": 1.5}
    factor = base_factors[traffic_level]
    
    # Adjust for peak times
    if day_type == "peak":
        if time_slot in ["morning", "evening"]:
            factor *= 1.3
        elif time_slot == "afternoon":
            factor *= 1.1
    
    return factor
