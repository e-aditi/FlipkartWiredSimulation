import pandas as pd
import random
from model import generate_orders, assign_riders, compute_kpis
from definitions import Zone, Customer, Rider
from cityProfiles import city_metadata
from dataGen import estimate_zone_count, generate_zones, distribute_riders_across_zones

def create_zones_from_city(city_name):
    """Generate zones based on city metadata"""
    if city_name not in city_metadata:
        raise ValueError(f"City {city_name} not found in metadata")
    
    metadata = city_metadata[city_name]
    num_zones = estimate_zone_count(metadata["area_sq_km"], metadata["avg_zone_size"])
    zone_data = generate_zones(num_zones)
    
    # Fixed riders per city (distributed across zones)
    fixed_riders_per_city = 15
    riders_distribution = distribute_riders_across_zones(fixed_riders_per_city, num_zones)
    
    zones = []
    for i, (zone_name, details) in enumerate(zone_data.items()):
        zone = Zone(zone_name)
        
        # Create customers
        for j in range(details["num_customers"]):
            customer = Customer(
                id=f"{zone_name}_C{j}", 
                zone=zone_name, 
                has_wallet=random.choice([True, False]), 
                wishlist_items=[f"item_{k}" for k in range(1, random.randint(2, 6))]
            )
            zone.customers.append(customer)
        
        # Create fixed riders using distributed count
        num_riders_for_zone = riders_distribution[i]
        for j in range(num_riders_for_zone):
            rider = Rider(id=f"{zone_name}_R{j}", zone=zone_name, rider_type="fixed")
            zone.riders.append(rider)
        
        zones.append(zone)
    
    return zones

def get_scenario_multiplier(scenario_type, time_slot=None):
    """Get volume multiplier based on scenario type"""
    multipliers = {
        "bau": 1.0,  # Business As Usual
        "peak_hours": 1.08,  # 8% higher than average
        "peak_days": 1.22,   # 22% higher than BAU
        "event_sale": 1.45,  # 45% higher than BAU
        "peak_hour_event": 3.0  # 200% higher (300% of BAU)
    }
    
    # For peak hours, check if it's morning or evening peak
    if scenario_type == "peak_hours" and time_slot:
        if time_slot in ["morning_peak", "evening_peak"]:
            return multipliers["peak_hours"]
        else:
            return multipliers["bau"]
    
    return multipliers.get(scenario_type, 1.0)

def run_simulation(city_name, scenario_type, time_slot=None):
    """Run the complete simulation with new scenario-based approach"""
    zones = create_zones_from_city(city_name)
    city_meta = city_metadata[city_name]
    results = {}
    
    # Get volume multiplier based on scenario
    volume_multiplier = get_scenario_multiplier(scenario_type, time_slot)
    
    # Store zone data for traffic factor calculation
    zone_data = {}
    metadata = city_metadata[city_name]
    num_zones = estimate_zone_count(metadata["area_sq_km"], metadata["avg_zone_size"])
    zone_traffic_data = generate_zones(num_zones)
    
    # First pass: Generate orders for all zones
    total_city_orders = 0
    for i, zone in enumerate(zones):
        # Get traffic factor using the zone's assigned traffic level
        zone_name = f"Zone_{i+1}"  # Match the zone naming convention
        if zone_name in zone_traffic_data:
            zone_traffic_level = zone_traffic_data[zone_name]["traffic_level"]
        else:
            zone_traffic_level = "moderate"  # Default fallback
        
        # Calculate traffic factor based on scenario
        base_traffic_factor = get_base_traffic_factor(zone_traffic_level)
        final_traffic_factor = base_traffic_factor * volume_multiplier
        
        # Generate orders with scenario-based volume
        zone.orders = generate_orders(
            zone.customers, scenario_type, time_slot, final_traffic_factor, volume_multiplier
        )
        total_city_orders += len(zone.orders)
    
    # Second pass: Add on-demand riders if needed and assign orders
    for i, zone in enumerate(zones):
        # Add on-demand riders if total city orders > 300
        add_on_demand_riders(zone, total_city_orders)
        
        # Get traffic factor again
        zone_name = f"Zone_{i+1}"  # Match the zone naming convention
        if zone_name in zone_traffic_data:
            zone_traffic_level = zone_traffic_data[zone_name]["traffic_level"]
        else:
            zone_traffic_level = "moderate"  # Default fallback
            
        base_traffic_factor = get_base_traffic_factor(zone_traffic_level)
        final_traffic_factor = base_traffic_factor * volume_multiplier
        
        # Assign riders with capacity limits
        assign_riders(
            zone, scenario_type, time_slot, final_traffic_factor, 
            city_meta["base_delivery_time"]
        )
        
        # Compute KPIs
        results[zone.name] = compute_kpis(zone, total_city_orders)
    
    return pd.DataFrame(results).T

def get_base_traffic_factor(traffic_level):
    """Get base traffic factor for zone traffic level"""
    base_factors = {"low": 1.0, "moderate": 1.2, "high": 1.5}
    return base_factors.get(traffic_level, 1.0)

def add_on_demand_riders(zone, total_orders_city_wide):
    """Add on-demand riders if total city orders exceed 300"""
    if total_orders_city_wide > 300:
        # Calculate how many additional riders needed
        additional_riders_needed = 1  # As specified, increase by 1
        
        # Add on-demand riders to the zone
        current_on_demand_count = len([r for r in zone.riders if r.rider_type == "on_demand"])
        for i in range(additional_riders_needed):
            rider_id = f"{zone.name}_OD{current_on_demand_count + i + 1}"
            on_demand_rider = Rider(id=rider_id, zone=zone.name, rider_type="on_demand")
            zone.riders.append(on_demand_rider)
    """Get base traffic factor for zone traffic level"""
    #base_factors = {"low": 1.0, "moderate": 1.2, "high": 1.5}
    #return base_factors.get(traffic_level, 1.0)

def get_yearly_breakdown():
    """Return the breakdown of different day types in a year"""
    return {
        "total_days": 365,
        "big_event_days": 1,      # 1 big event day (peak_hour_event)
        "sale_days": 12,          # 12 sale days (event_sale)
        "peak_days_per_week": 3,  # Fri, Sat, Sun (peak_days)
        "peak_days_yearly": 3 * 52,  # 156 peak days (Fri, Sat, Sun)
        "bau_days": 365 - 1 - 12 - (3 * 52),  # Remaining BAU days
        "peak_hours_per_day": 2   # Morning and evening peak hours
    }

def simulate_yearly_patterns(city_name):
    """Simulate different patterns throughout the year"""
    yearly_data = get_yearly_breakdown()
    results = {}
    
    # Simulate BAU days
    print(f"Simulating {yearly_data['bau_days']} BAU days...")
    results['BAU'] = run_simulation(city_name, "bau")
    
    # Simulate peak days (Fri, Sat, Sun)
    print(f"Simulating {yearly_data['peak_days_yearly']} peak days...")
    results['Peak Days'] = run_simulation(city_name, "peak_days")
    
    # Simulate sale/event days
    print(f"Simulating {yearly_data['sale_days']} sale/event days...")
    results['Sale Days'] = run_simulation(city_name, "event_sale")
    
    # Simulate big event day
    print("Simulating 1 big event day...")
    results['Big Event Day'] = run_simulation(city_name, "peak_hour_event")
    
    # Simulate peak hours scenarios
    print("Simulating peak hours scenarios...")
    results['Morning Peak Hours'] = run_simulation(city_name, "peak_hours", "morning_peak")
    results['Evening Peak Hours'] = run_simulation(city_name, "peak_hours", "evening_peak")
    
    return results