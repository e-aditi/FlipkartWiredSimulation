# main.py - Integrated Delivery Simulation System

import json
import random
import pandas as pd
from datetime import datetime, timedelta

# ============ CITY PROFILES ============
city_metadata = {
    "Pune": {
        "avg_zone_size": 50,
        "base_delivery_time": 8,
        "area_sq_km": 331.3
    },
    "Delhi": {
        "avg_zone_size": 40,
        "base_delivery_time": 10,
        "area_sq_km": 1484
    },
    "Mumbai": {
        "avg_zone_size": 35,
        "base_delivery_time": 12,
        "area_sq_km": 603
    }
}

# ============ DATA GENERATION ============
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
            "num_customers": random.randint(50, 200),
            "num_riders": random.randint(5, 15)
        }
    return zones

# ============ DEFINITIONS ============
class Customer:
    def __init__(self, id, zone, has_wallet, wishlist_items):
        self.id = id
        self.zone = zone
        self.has_wallet = has_wallet
        self.wishlist_items = wishlist_items
        self.cart = []

class Order:
    def __init__(self, customer, items, scheduled, timestamp):
        self.customer = customer
        self.items = items
        self.scheduled = scheduled
        self.timestamp = timestamp
        self.delivery_time = None

class Rider:
    def __init__(self, id, zone):
        self.id = id
        self.zone = zone
        self.available = True
        self.orders_delivered = 0

class Zone:
    def __init__(self, name):
        self.name = name
        self.customers = []
        self.riders = []
        self.orders = []

# ============ MODEL LOGIC ============
def generate_orders(customers, day_type, time_slot, traffic_factor):
    orders = []
    base_prob = 0.3
    
    if day_type == "peak" and time_slot in ["morning", "evening"]:
        base_prob *= 1.5

    for customer in customers:
        if day_type == "non_peak" and customer.has_wallet:
            items = customer.wishlist_items[:random.randint(1, len(customer.wishlist_items))]
            orders.append(Order(customer, items, scheduled=True, timestamp=datetime.now()))
        else:
            if random.random() < base_prob:
                items = ["item_" + str(random.randint(1, 10)) for _ in range(random.randint(1, 3))]
                orders.append(Order(customer, items, scheduled=False, timestamp=datetime.now()))
    return orders

def assign_riders(zone, day_type, time_slot, traffic_factor, base_delivery_time):
    for order in zone.orders:
        available_riders = [r for r in zone.riders if r.available]
        if available_riders:
            rider = random.choice(available_riders)
            rider.available = False
            rider.orders_delivered += 1
            
            # Calculate delivery time based on traffic and base time
            base_time = base_delivery_time + random.randint(-2, 5)
            adjusted_time = int(base_time * traffic_factor)
            order.delivery_time = order.timestamp + timedelta(minutes=adjusted_time)
            rider.available = True

def compute_kpis(zone):
    total_orders = len(zone.orders)
    if total_orders == 0:
        return {
            "Total Orders": 0,
            "SLA <10 mins": 0,
            "Avg OPH": 0,
            "Rider Utilization": 0,
            "Cost/Delivery": 50
        }
    
    delivered_under_10 = sum(1 for o in zone.orders if o.delivery_time and (o.delivery_time - o.timestamp).seconds <= 600)
    avg_oph = total_orders / len(zone.riders) if zone.riders else 0
    total_delivered = sum(r.orders_delivered for r in zone.riders)
    rider_utilization = total_delivered / (len(zone.riders) * total_orders) if zone.riders and total_orders else 0
    cost_per_delivery = 50 - (5 * rider_utilization)

    return {
        "Total Orders": total_orders,
        "SLA <10 mins": delivered_under_10,
        "Avg OPH": round(avg_oph, 2),
        "Rider Utilization": round(rider_utilization * 100, 2),  # Percentage
        "Cost/Delivery": round(cost_per_delivery, 2)
    }

# ============ INTEGRATION LAYER ============
def create_zones_from_city(city_name):
    """Generate zones based on city metadata"""
    if city_name not in city_metadata:
        raise ValueError(f"City {city_name} not found in metadata")
    
    metadata = city_metadata[city_name]
    num_zones = estimate_zone_count(metadata["area_sq_km"], metadata["avg_zone_size"])
    zone_data = generate_zones(num_zones)
    
    zones = []
    for zone_name, details in zone_data.items():
        zone = Zone(zone_name)
        
        # Create customers
        for i in range(details["num_customers"]):
            customer = Customer(
                id=f"{zone_name}_C{i}", 
                zone=zone_name, 
                has_wallet=random.choice([True, False]), 
                wishlist_items=[f"item_{j}" for j in range(1, random.randint(2, 6))]
            )
            zone.customers.append(customer)
        
        # Create riders
        for i in range(details["num_riders"]):
            rider = Rider(id=f"{zone_name}_R{i}", zone=zone_name)
            zone.riders.append(rider)
        
        zones.append(zone)
    
    return zones

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

def run_simulation(city_name, day_type, time_slot):
    """Run the complete simulation"""
    zones = create_zones_from_city(city_name)
    city_meta = city_metadata[city_name]
    results = {}
    
    for zone in zones:
        # Get traffic factor for this zone
        traffic_factor = get_traffic_factor(
            assign_traffic_level(), day_type, time_slot
        )
        
        # Generate orders
        zone.orders = generate_orders(
            zone.customers, day_type, time_slot, traffic_factor
        )
        
        # Assign riders
        assign_riders(
            zone, day_type, time_slot, traffic_factor, 
            city_meta["base_delivery_time"]
        )
        
        # Compute KPIs
        results[zone.name] = compute_kpis(zone)
    
    return pd.DataFrame(results).T

# ============ CONSOLE INTERFACE ============
def print_banner():
    print("=" * 60)
    print("          DELIVERY SIMULATION SYSTEM")
    print("=" * 60)

def get_user_inputs():
    """Get simulation parameters from user"""
    print("\nAvailable Cities:")
    for i, city in enumerate(city_metadata.keys(), 1):
        area = city_metadata[city]["area_sq_km"]
        zones = estimate_zone_count(area, city_metadata[city]["avg_zone_size"])
        print(f"{i}. {city} (Area: {area} sq km, ~{zones} zones)")
    
    while True:
        try:
            city_choice = int(input("\nSelect city (number): ")) - 1
            city_name = list(city_metadata.keys())[city_choice]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")
    
    print(f"\nSelected City: {city_name}")
    
    print("\nDay Types:")
    print("1. Peak Day")
    print("2. Non-Peak Day")
    while True:
        try:
            day_choice = int(input("Select day type (1-2): "))
            day_type = "peak" if day_choice == 1 else "non_peak"
            break
        except ValueError:
            print("Invalid choice. Please enter 1 or 2.")
    
    print("\nTime Slots:")
    print("1. Morning")
    print("2. Afternoon") 
    print("3. Evening")
    while True:
        try:
            time_choice = int(input("Select time slot (1-3): "))
            time_slots = ["morning", "afternoon", "evening"]
            time_slot = time_slots[time_choice - 1]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please enter 1-3.")
    
    return city_name, day_type, time_slot

def print_results(results, city_name, day_type, time_slot):
    """Print simulation results in a formatted way"""
    print("\n" + "=" * 80)
    print(f"SIMULATION RESULTS")
    print("=" * 80)
    print(f"City: {city_name}")
    print(f"Day Type: {day_type.title()}")
    print(f"Time Slot: {time_slot.title()}")
    print(f"Total Zones Simulated: {len(results)}")
    print("-" * 80)
    
    # Print detailed results
    print(f"{'Zone':<12} {'Orders':<8} {'SLA<10min':<9} {'Avg OPH':<8} {'Util %':<8} {'Cost/Del':<8}")
    print("-" * 80)
    
    for zone_name, metrics in results.iterrows():
        print(f"{zone_name:<12} {metrics['Total Orders']:<8} "
              f"{metrics['SLA <10 mins']:<9} {metrics['Avg OPH']:<8} "
              f"{metrics['Rider Utilization']:<8} ₹{metrics['Cost/Delivery']:<7}")
    
    # Print summary statistics
    print("-" * 80)
    print("CITY SUMMARY:")
    print(f"Total Orders: {results['Total Orders'].sum()}")
    print(f"Average SLA Performance: {results['SLA <10 mins'].mean():.1f} orders/zone")
    print(f"Average OPH: {results['Avg OPH'].mean():.2f}")
    print(f"Average Rider Utilization: {results['Rider Utilization'].mean():.1f}%")
    print(f"Average Cost per Delivery: ₹{results['Cost/Delivery'].mean():.2f}")
    print("=" * 80)

def main():
    """Main execution function"""
    print_banner()
    
    while True:
        try:
            city_name, day_type, time_slot = get_user_inputs()
            
            print(f"\nRunning simulation for {city_name}...")
            print("Please wait...")
            
            # Run simulation
            results = run_simulation(city_name, day_type, time_slot)
            
            # Print results
            print_results(results, city_name, day_type, time_slot)
            
            # Ask if user wants to run another simulation
            again = input("\nRun another simulation? (y/n): ").lower()
            if again != 'y':
                break
                
        except KeyboardInterrupt:
            print("\nSimulation interrupted by user.")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            print("Please try again.")
    
    print("\nThank you for using the Delivery Simulation System!")

if __name__ == "__main__":
    main()