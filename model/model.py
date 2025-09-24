from datetime import datetime, timedelta
import random
from definitions import Order

def generate_orders(customers, scenario_type, time_slot, final_traffic_factor, volume_multiplier):
    """Generate orders based on scenario type and volume multiplier"""
    orders = []
    
    # Base probability for order generation
    base_prob = get_base_probability(scenario_type, time_slot)
    
    # Adjust probability based on volume multiplier
    adjusted_prob = min(base_prob * volume_multiplier, 0.95)  # Cap at 95%
    
    for customer in customers:
        # Generate orders based on scenario-specific logic
        if should_generate_order(customer, scenario_type, adjusted_prob):
            items = get_order_items(customer, scenario_type)
            is_scheduled = is_order_scheduled(scenario_type)
            
            order = Order(
                customer=customer, 
                items=items, 
                scheduled=is_scheduled, 
                timestamp=datetime.now()
            )
            orders.append(order)
    
    return orders

def get_base_probability(scenario_type, time_slot):
    """Get base probability for order generation based on scenario"""
    # probabilities = {
    #    "bau": 0.25,
    #    "peak_hours": 0.30,
    #    "peak_days": 0.35,
    #    "event_sale": 0.45,
    #    "peak_hour_event": 0.65
    # }

    probabilities = {
        "bau": 0.35,
        "peak_hours": 0.25,
        "peak_days": 0.30,
        "event_sale": 0.45,
        "peak_hour_event": 0.60
    }
    
    # Adjust for specific time slots during peak hours
    if scenario_type == "peak_hours":
        if time_slot == "morning_peak":  # 07:00-11:00
            return probabilities["peak_hours"] * 1.2
        elif time_slot == "evening_peak":  # 19:00-23:00
            return probabilities["peak_hours"] * 1.3
        else:
            return probabilities["bau"]
    
    return probabilities.get(scenario_type, 0.25)

def should_generate_order(customer, scenario_type, probability):
    """Determine if a customer should place an order"""
    # Base random check
    if random.random() > probability:
        return False
    
    # Scenario-specific logic
    if scenario_type == "bau":
        # Regular behavior - wallet users more likely to order
        return customer.has_wallet or random.random() < 0.3
    
    elif scenario_type == "peak_hours":
        # Peak hours - higher chance for all customers
        return random.random() < 0.8
    
    elif scenario_type == "peak_days":
        # Weekend/peak days - more leisure orders
        return random.random() < 0.75
    
    elif scenario_type == "event_sale":
        # Sale days - everyone more likely to order
        return random.random() < 0.85
    
    elif scenario_type == "peak_hour_event":
        # Big event - almost everyone orders
        return random.random() < 0.9
    
    return True

def get_order_items(customer, scenario_type):
    """Get items for order based on scenario type"""
    if scenario_type in ["event_sale", "peak_hour_event"]:
        # During sales/events, customers order more items
        if customer.wishlist_items and random.random() < 0.7:
            # 70% chance to order from wishlist during events
            num_items = min(len(customer.wishlist_items), random.randint(2, 5))
            return random.sample(customer.wishlist_items, num_items)
        else:
            # Order random items (more during events)
            return [f"item_{random.randint(1, 20)}" for _ in range(random.randint(2, 6))]
    
    elif scenario_type == "peak_days":
        # Weekend orders - mix of wishlist and random
        if customer.wishlist_items and random.random() < 0.5:
            num_items = min(len(customer.wishlist_items), random.randint(1, 3))
            return random.sample(customer.wishlist_items, num_items)
        else:
            return [f"item_{random.randint(1, 15)}" for _ in range(random.randint(1, 4))]
    
    else:
        # BAU and peak hours - regular order size
        if customer.wishlist_items and random.random() < 0.4:
            num_items = min(len(customer.wishlist_items), random.randint(1, 2))
            return random.sample(customer.wishlist_items, num_items)
        else:
            return [f"item_{random.randint(1, 10)}" for _ in range(random.randint(1, 3))]

def is_order_scheduled(scenario_type):
    """Determine if order is scheduled based on scenario"""
    if scenario_type == "bau":
        return random.random() < 0.3  # 30% scheduled during BAU
    elif scenario_type in ["event_sale", "peak_hour_event"]:
        return random.random() < 0.1  # 10% scheduled during events (more urgent)
    else:
        return random.random() < 0.2  # 20% scheduled during other scenarios

def assign_riders(zone, scenario_type, time_slot, traffic_factor, base_delivery_time):
    """Assign riders to orders with capacity limits and scenario-specific delivery time calculation"""
    max_orders_per_rider = 20  # Maximum orders a rider can handle per day
    
    # Reset all rider capacities
    for rider in zone.riders:
        rider.orders_delivered = 0
        rider.available = True
    
    unassigned_orders = []
    
    for order in zone.orders:
        # Find available riders with capacity
        available_riders = [
            r for r in zone.riders 
            if r.available and r.orders_delivered < max_orders_per_rider
        ]
        
        if available_riders:
            # Assign to rider with least orders (load balancing)
            rider = min(available_riders, key=lambda r: r.orders_delivered)
            rider.orders_delivered += 1
            
            # Calculate delivery time based on scenario and traffic
            delivery_minutes = calculate_delivery_time(
                scenario_type, time_slot, traffic_factor, base_delivery_time
            )
            
            order.delivery_time = order.timestamp + timedelta(minutes=delivery_minutes)
            order.assigned_rider = rider.id
            
            # Mark rider as temporarily unavailable if at capacity
            if rider.orders_delivered >= max_orders_per_rider:
                rider.available = False
        else:
            # No available riders - order remains unassigned
            unassigned_orders.append(order)
            order.delivery_time = None
            order.assigned_rider = None
    
    # Store unassigned orders info
    zone.unassigned_orders = unassigned_orders

def calculate_delivery_time(scenario_type, time_slot, traffic_factor, base_delivery_time):
    """Calculate delivery time based on scenario-specific factors"""
    # Start with base delivery time
    base_time = base_delivery_time + random.randint(-2, 3)
    
    # Scenario-specific adjustments
    if scenario_type == "peak_hour_event":
        # Big event - significantly longer delivery times due to high volume
        base_time *= 2.5
    elif scenario_type == "event_sale":
        # Sale days - longer delivery times
        base_time *= 1.8
    elif scenario_type == "peak_days":
        # Weekend/peak days - moderately longer
        base_time *= 1.4
    elif scenario_type == "peak_hours":
        # Peak hours - slight increase
        if time_slot == "evening_peak":
            base_time *= 1.3  # Evening peak is busier
        elif time_slot == "morning_peak":
            base_time *= 1.2
    
    # Apply traffic factor
    final_time = int(base_time * traffic_factor)
    
    # Add some randomness but keep realistic bounds
    final_time += random.randint(-1, 3)
    
    # Ensure minimum delivery time
    return max(final_time, 5)

def compute_kpis(zone, total_city_orders=0):
    """Compute KPIs for the zone with new rider utilization logic"""
    total_orders = len(zone.orders)
    unassigned_orders = len(getattr(zone, 'unassigned_orders', []))
    assigned_orders = total_orders - unassigned_orders
    
    if total_orders == 0:
        return {
            "Total Orders": 0,
            "Assigned Orders": 0,
            "Unassigned Orders": 0,
            "SLA <10 mins": 0,
            "Avg OPH": 0,
            "Rider Utilization": 0,
            "Fixed Riders": 0,
            "On-Demand Riders": 0,
            "Cost/Delivery": 0
        }
    
    # Count orders delivered under 10 minutes (only assigned orders)
    delivered_under_10 = sum(
        1 for o in zone.orders 
        if o.delivery_time and (o.delivery_time - o.timestamp).total_seconds() <= 600
    )
    
    # Count rider types
    fixed_riders = len([r for r in zone.riders if r.rider_type == "fixed"])
    on_demand_riders = len([r for r in zone.riders if r.rider_type == "on_demand"])
    total_riders = len(zone.riders)
    
    # Calculate rider utilization based on 20 orders per rider = 100%
    max_orders_per_rider = 20
    total_possible_orders = total_riders * max_orders_per_rider
    total_delivered = sum(r.orders_delivered for r in zone.riders)
    
    # Utilization = (actual orders delivered / max possible orders) * 100
    rider_utilization = (total_delivered / total_possible_orders) * 100 if total_possible_orders > 0 else 0
    
    # Calculate average orders per hour per rider (assuming 8-hour working day)
    avg_oph = total_delivered / (total_riders * 8) if total_riders > 0 else 0
    
    # Calculate cost per delivery
    # Fixed riders: ₹400/day (₹50/hour * 8 hours)
    # On-demand riders: ₹500/day (higher cost for flexibility)
    # Variable cost: ₹15 per delivery
    fixed_rider_cost = fixed_riders * 400
    on_demand_rider_cost = on_demand_riders * 500
    variable_cost = assigned_orders * 15
    total_cost = fixed_rider_cost + on_demand_rider_cost + variable_cost
    
    cost_per_delivery = total_cost / assigned_orders if assigned_orders > 0 else 0
    
    return {
        "Total Orders": total_orders,
        "Assigned Orders": assigned_orders,
        "Unassigned Orders": unassigned_orders,
        "SLA <10 mins": delivered_under_10,
        "Avg OPH": round(avg_oph, 2),
        "Rider Utilization": round(rider_utilization, 2),  # Percentage based on 20 orders = 100%
        "Fixed Riders": fixed_riders,
        "On-Demand Riders": on_demand_riders,
        "Cost/Delivery": round(cost_per_delivery, 2)
    }