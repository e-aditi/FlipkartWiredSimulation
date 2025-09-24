from cityProfiles import city_metadata
from dataGen import estimate_zone_count
from interaction import run_simulation, simulate_yearly_patterns, get_yearly_breakdown

def print_banner():
    print("=" * 80)
    print("          DELIVERY FLEET OPTIMIZATION SIMULATION          ")
    print("=" * 80)

def get_user_inputs():
    """Get simulation parameters from user"""
    print("\nAvailable Cities:")
    for i, city in enumerate(city_metadata.keys(), 1):
        area = city_metadata[city]["area_sq_km"]
        zones = estimate_zone_count(area, city_metadata[city]["avg_zone_size"])
        riders = city_metadata[city]["total_riders"]
        print(f"{i}. {city} (Area: {area} sq km, ~{zones} zones, {riders} riders)")
    
    while True:
        try:
            city_choice = int(input("\nSelect city (number): ")) - 1
            city_name = list(city_metadata.keys())[city_choice]
            break
        except (ValueError, IndexError):
            print("Invalid choice. Please try again.")
    
    print(f"\nSelected City: {city_name}")
    
    print("\nSimulation Scenarios:")
    print("1. Peak Hours (Morning: 07:00-11:00 & Evening: 19:00-23:00) - 8% higher volume")
    print("2. Peak Days (Fri, Sat, Sun) - 22% higher volume")
    print("3. Event/Sale Days - 45% higher volume")
    print("4. Peak Hour of Event Day - 200% higher volume")
    print("5. Business As Usual (BAU)")
    print("6. Yearly Pattern Analysis (All scenarios)")
    
    while True:
        try:
            scenario_choice = int(input("Select scenario (1-6): "))
            if 1 <= scenario_choice <= 6:
                break
            print("Invalid choice. Please enter 1-6.")
        except ValueError:
            print("Invalid choice. Please enter a number.")
    
    scenario_mapping = {
        1: "peak_hours",
        2: "peak_days", 
        3: "event_sale",
        4: "peak_hour_event",
        5: "bau",
        6: "yearly_analysis"
    }
    
    scenario_type = scenario_mapping[scenario_choice]
    time_slot = None
    
    # For peak hours, ask for specific time slot
    if scenario_type == "peak_hours":
        print("\nPeak Hour Time Slots:")
        print("1. Morning Peak (07:00-11:00)")
        print("2. Evening Peak (19:00-23:00)")
        while True:
            try:
                time_choice = int(input("Select time slot (1-2): "))
                time_slot = "morning_peak" if time_choice == 1 else "evening_peak"
                break
            except ValueError:
                print("Invalid choice. Please enter 1 or 2.")
    
    return city_name, scenario_type, time_slot

def print_scenario_info(scenario_type, time_slot=None):
    """Print information about the selected scenario"""
    scenario_info = {
        "bau": "Business As Usual - Normal day operations",
        "peak_hours": f"Peak Hours - {'Morning (07:00-11:00)' if time_slot == 'morning_peak' else 'Evening (19:00-23:00)'} - 8% higher volume",
        "peak_days": "Peak Days (Fri, Sat, Sun) - 22% higher volume than BAU",
        "event_sale": "Event/Sale Days - 45% higher volume than BAU",
        "peak_hour_event": "Peak Hour of Event Day - 200% higher volume than BAU"
    }
    
    print(f"\nScenario: {scenario_info.get(scenario_type, 'Unknown scenario')}")

def print_results(results, city_name, scenario_type, time_slot=None):
    """Print simulation results in a formatted way"""
    print("\n" + "=" * 90)
    print(f"SIMULATION RESULTS")
    print("=" * 90)
    print(f"City: {city_name}")
    print_scenario_info(scenario_type, time_slot)
    print(f"Total Zones Simulated: {len(results)}")
    print("-" * 90)
    
    # Print detailed results
    print(f"{'Zone':<12} {'Orders':<8} {'Assigned':<9} {'Unassigned':<11} {'SLA<10min':<9} {'Avg OPH':<8} {'Util %':<8} {'Fixed R':<8} {'OD R':<5} {'Cost/Del':<9}")
    print("-" * 110)
    
    for zone_name, metrics in results.iterrows():
        print(f"{zone_name:<12} {metrics['Total Orders']:<8} {metrics['Assigned Orders']:<9} "
              f"{metrics['Unassigned Orders']:<11} {metrics['SLA <10 mins']:<9} "
              f"{metrics['Avg OPH']:<8.2f} {metrics['Rider Utilization']:<8.1f} "
              f"{metrics['Fixed Riders']:<8} {metrics['On-Demand Riders']:<5} ₹{metrics['Cost/Delivery']:<8.2f}")
    
    # Print summary statistics
    print("-" * 110)
    print("CITY SUMMARY:")
    print(f"Total Orders: {results['Total Orders'].sum()}")
    print(f"Total Assigned Orders: {results['Assigned Orders'].sum()}")
    print(f"Total Unassigned Orders: {results['Unassigned Orders'].sum()}")
    print(f"Assignment Rate: {(results['Assigned Orders'].sum()/results['Total Orders'].sum()*100):.1f}%")
    print(f"Average SLA Performance: {results['SLA <10 mins'].mean():.1f} orders/zone")
    print(f"Average OPH: {results['Avg OPH'].mean():.2f}")
    print(f"Average Rider Utilization: {results['Rider Utilization'].mean():.1f}% (Max: 20 orders = 100%)")
    print(f"Total Fixed Riders: {results['Fixed Riders'].sum()}")
    print(f"Total On-Demand Riders: {results['On-Demand Riders'].sum()}")
    print(f"Average Cost per Delivery: ₹{results['Cost/Delivery'].mean():.2f}")
    print("=" * 110)

def print_yearly_analysis(results_dict, city_name):
    """Print yearly pattern analysis results"""
    print("\n" + "=" * 100)
    print(f"YEARLY PATTERN ANALYSIS FOR {city_name.upper()}")
    print("=" * 100)
    
    yearly_breakdown = get_yearly_breakdown()
    print(f"Year Breakdown:")
    print(f"  • BAU Days: {yearly_breakdown['bau_days']} days")
    print(f"  • Peak Days (Fri-Sun): {yearly_breakdown['peak_days_yearly']} days")
    print(f"  • Sale/Event Days: {yearly_breakdown['sale_days']} days")
    print(f"  • Big Event Day: {yearly_breakdown['big_event_days']} day")
    print("-" * 100)
    
    # Compare scenarios
    print(f"{'Scenario':<20} {'Avg Orders':<11} {'Assignment%':<12} {'Avg SLA<10':<10} {'Avg OPH':<9} {'Avg Util%':<10} {'Avg Cost':<10}")
    print("-" * 110)
    
    for scenario_name, results in results_dict.items():
        avg_orders = results['Total Orders'].mean()
        assignment_rate = (results['Assigned Orders'].sum() / results['Total Orders'].sum() * 100) if results['Total Orders'].sum() > 0 else 0
        avg_sla = results['SLA <10 mins'].mean()
        avg_oph = results['Avg OPH'].mean()
        avg_util = results['Rider Utilization'].mean()
        avg_cost = results['Cost/Delivery'].mean()
        
        print(f"{scenario_name:<20} {avg_orders:<11.1f} {assignment_rate:<12.1f} {avg_sla:<10.1f} {avg_oph:<9.2f} {avg_util:<10.1f} ₹{avg_cost:<9.2f}")
    
    print("=" * 110)
    
    # Calculate yearly projections
    yearly_orders = (
        yearly_breakdown['bau_days'] * results_dict['BAU']['Total Orders'].sum() +
        yearly_breakdown['peak_days_yearly'] * results_dict['Peak Days']['Total Orders'].sum() +
        yearly_breakdown['sale_days'] * results_dict['Sale Days']['Total Orders'].sum() +
        yearly_breakdown['big_event_days'] * results_dict['Big Event Day']['Total Orders'].sum()
    )
    
    print(f"\nYEARLY PROJECTIONS:")
    print(f"Total Orders per Year: {yearly_orders:,.0f}")
    print(f"Average Orders per Day: {yearly_orders/365:,.0f}")
    print("=" * 100)

def main():
    """Main execution function"""
    print_banner()
    
    while True:
        try:
            city_name, scenario_type, time_slot = get_user_inputs()
            
            if scenario_type == "yearly_analysis":
                print(f"\nRunning yearly pattern analysis for {city_name}...")
                print("This will simulate all scenarios. Please wait...")
                
                results_dict = simulate_yearly_patterns(city_name)
                print_yearly_analysis(results_dict, city_name)
            else:
                print(f"\nRunning simulation for {city_name}...")
                print("Please wait...")
                
                # Run simulation
                results = run_simulation(city_name, scenario_type, time_slot)
                
                # Print results
                print_results(results, city_name, scenario_type, time_slot)
            
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
    
    print("\nSimulation completed!")

if __name__ == "__main__":
    main()