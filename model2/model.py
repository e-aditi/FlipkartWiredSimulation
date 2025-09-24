import math
import time
import pandas as pd
from datetime import datetime
import os

# Meta Data
max_orders_per_day = 32
dark_store_radius_km = 3
dark_store_area = math.pi * (dark_store_radius_km ** 2)
base_delivery_time = 10

city_metadata = {
    "Delhi": {
        "area_sq_km": 141,
        "fixed_riders": 75,
        "dark_stores": 16,
        "traffic_factor": 5,
        "BAU_order_per_hour_non_peak": 868,
        "peakday_order_per_hour_non_peak": 1085,
        "monthpeak_order_per_hour_non_peak": 1229,
        "yearpeak_order_per_hour_non_peak": 2604,
        "BAU_order_per_hour_peak": 940,
        "peakday_order_per_hour_peak": 1157,
        "monthpeak_order_per_hour_peak": 1374,
        "yearpeak_order_per_hour_peak": 2821
    },
    "Pune": {
        "area_sq_km": 10,
        "fixed_riders": 30,
        "dark_stores": 2,
        "traffic_factor": 3,
        "BAU_order_per_hour_non_peak": 416,
        "peakday_order_per_hour_non_peak": 520,
        "monthpeak_order_per_hour_non_peak": 590,
        "yearpeak_order_per_hour_non_peak": 1250,
        "BAU_order_per_hour_peak": 451,
        "peakday_order_per_hour_peak": 555,
        "monthpeak_order_per_hour_peak": 659,
        "yearpeak_order_per_hour_peak": 1354
    }
}

# Constants for simulation
hours_per_day = 16
peak_hours = 8
non_peak_hours = 8

# Options mapping
options_map = {
    "a": "BAU",
    "b": "peakday", 
    "c": "monthpeak",
    "d": "yearpeak",
    "e": "all"
}

class FlipkartRiderSimulation:
    def __init__(self, city_metadata):
        self.city_metadata = city_metadata
        self.simulation_results = []
        
    def clear_screen(self):
        """Clear console for better display"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, option_type):
        """Print formatted header for simulation"""
        print("=" * 100)
        print(f"🚀 FLIPKART QUICK COMMERCE - RIDER OPTIMIZATION SIMULATION")
        print(f"📊 Simulation Type: {options_map.get(option_type, option_type).upper()}")
        print(f"🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 100)
    
    def print_city_header(self, city):
        """Print city-specific header"""
        city_data = self.city_metadata[city]
        print(f"\n📍 CITY: {city.upper()}")
        print(f"   Fixed Riders: {city_data['fixed_riders']} | Dark Stores: {city_data['dark_stores']} | Traffic Factor: {city_data['traffic_factor']}")
        print("-" * 100)
        print(f"{'Hour':<4} | {'Period':<10} | {'Orders':<7} | {'Fixed Used':<11} | {'Adhoc Used':<11} | {'OPH':<6} | {'Fixed Util %':<12}")
        print("-" * 100)
    
    def calculate_metrics(self, orders, city_data):
        """Calculate rider metrics based on algorithm"""
        fixed_riders_used = min(orders // 2, city_data["fixed_riders"])
        adhoc_riders_used = max(0, orders - (fixed_riders_used * 2))
        total_riders = fixed_riders_used + adhoc_riders_used
        
        OPH = orders / total_riders if total_riders > 0 else 0
        fixed_utilization = (fixed_riders_used / city_data["fixed_riders"]) * 100 if city_data["fixed_riders"] > 0 else 0
        
        return {
            'fixed_riders_used': fixed_riders_used,
            'adhoc_riders_used': adhoc_riders_used,
            'total_riders': total_riders,
            'OPH': OPH,
            'fixed_utilization': fixed_utilization
        }
    
    def simulate_single_scenario(self, option):
        """Simulate a single scenario (BAU, peakday, etc.)"""
        scenario_name = options_map[option]
        self.print_header(option)
        
        all_city_results = {}
        
        for city in self.city_metadata:
            city_data = self.city_metadata[city]
            self.print_city_header(city)
            
            hourly_metrics = []
            
            for hour in range(1, hours_per_day + 1):
                # Determine if peak or non-peak hour
                if hour <= peak_hours:
                    period = "PEAK"
                    order_key = f"{scenario_name}_order_per_hour_peak"
                else:
                    period = "NON-PEAK"
                    order_key = f"{scenario_name}_order_per_hour_non_peak"
                
                orders = city_data[order_key]
                metrics = self.calculate_metrics(orders, city_data)
                
                # Display real-time data
                print(f"{hour:<4} | {period:<10} | {orders:<7} | {metrics['fixed_riders_used']:<11} | "
                      f"{metrics['adhoc_riders_used']:<11} | {metrics['OPH']:<6.2f} | {metrics['fixed_utilization']:<12.2f}")
                
                # Store for averaging
                hourly_metrics.append(metrics)
                
                # Store detailed results
                self.simulation_results.append({
                    'scenario': scenario_name,
                    'city': city,
                    'hour': hour,
                    'period': period,
                    'orders': orders,
                    **metrics
                })
                
                # Simulation delay (can be removed for faster execution)
                time.sleep(0.05)  # Reduced for competition demo
            
            # Calculate and display city averages
            avg_OPH = sum(m['OPH'] for m in hourly_metrics) / len(hourly_metrics)
            avg_fixed_util = sum(m['fixed_utilization'] for m in hourly_metrics) / len(hourly_metrics)
            
            all_city_results[city] = {
                'avg_OPH': avg_OPH,
                'avg_fixed_util': avg_fixed_util
            }
            
            print("-" * 100)
            print(f"📈 CITY SUMMARY - {city}")
            print(f"   Average OPH: {avg_OPH:.2f} | Average Fixed Utilization: {avg_fixed_util:.2f}%")
            print("-" * 100)
        
        return all_city_results
    
    def simulate_all_scenarios(self):
        """Simulate all scenarios for grand average"""
        print("🔄 RUNNING ALL SCENARIOS SIMULATION")
        print("=" * 100)
        
        all_results = {}
        grand_totals = {"total_OPH": 0, "total_fixed_util": 0, "count": 0}
        
        for opt in ["a", "b", "c", "d"]:
            print(f"\n🎯 Processing {options_map[opt].upper()} Scenario...")
            results = self.simulate_single_scenario(opt)
            all_results[opt] = results
            
            # Add to grand totals
            for city_result in results.values():
                grand_totals["total_OPH"] += city_result['avg_OPH']
                grand_totals["total_fixed_util"] += city_result['avg_fixed_util']
                grand_totals["count"] += 1
        
        # Calculate and display grand averages
        print("\n" + "=" * 100)
        print("🏆 GRAND SUMMARY - ALL SCENARIOS & CITIES")
        print("=" * 100)
        
        if grand_totals["count"] > 0:
            grand_avg_OPH = grand_totals["total_OPH"] / grand_totals["count"]
            grand_avg_fixed_util = grand_totals["total_fixed_util"] / grand_totals["count"]
            
            print(f"📊 Grand Average OPH: {grand_avg_OPH:.2f}")
            print(f"📊 Grand Average Fixed Utilization: {grand_avg_fixed_util:.2f}%")
        
        return all_results
    
    def export_results_to_csv(self):
        """Export detailed results to CSV for further analysis"""
        if self.simulation_results:
            df = pd.DataFrame(self.simulation_results)
            filename = f"flipkart_rider_simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"\n💾 Results exported to: {filename}")
            return filename
        return None
    
    def run_simulation(self, option="a"):
        """Main simulation runner"""
        self.simulation_results = []  # Reset results
        
        if option == "e":
            results = self.simulate_all_scenarios()
        else:
            results = self.simulate_single_scenario(option)
        
        # Export results
        csv_file = self.export_results_to_csv()
        
        return results, csv_file

# Interactive Menu System
def display_menu():
    print("\n" + "=" * 60)
    print("🏪 FLIPKART QUICK COMMERCE SIMULATION")
    print("=" * 60)
    print("Select simulation option:")
    print("a) BAU (Business as Usual)")
    print("b) Peak Day (22% higher than BAU)")
    print("c) Month Peak (45% higher than BAU)")
    print("d) Year Peak (200% higher than BAU)")
    print("e) All Scenarios (Grand Average)")
    print("=" * 60)

def main():
    """Main execution function"""
    # Initialize simulation
    sim = FlipkartRiderSimulation(city_metadata)
    
    # For competition demo, you can directly set the option
    # option = "e"  # Uncomment this line and comment the menu for direct execution
    
    # Interactive menu (comment this section for direct execution)
    display_menu()
    option = input("Enter your choice (a-e): ").lower().strip()
    
    if option not in ["a", "b", "c", "d", "e"]:
        print("❌ Invalid option. Defaulting to BAU (option 'a')")
        option = "a"
    
    # Run simulation
    print(f"\n🚀 Starting simulation for option: {option}")
    results, csv_file = sim.run_simulation(option)
    
    print(f"\n✅ Simulation completed successfully!")
    if csv_file:
        print(f"📁 Detailed results saved to: {csv_file}")

# Key Performance Indicators Summary
def print_kpi_summary():
    """Print KPIs for competition presentation"""
    print("\n" + "=" * 80)
    print("📊 KEY PERFORMANCE INDICATORS (KPIs)")
    print("=" * 80)
    print("1. Orders Per Hour (OPH): Efficiency metric for rider utilization")
    print("2. Fixed Utilization %: Percentage of fixed riders actively used")
    print("3. Adhoc Rider Dependency: Additional riders needed beyond fixed capacity")
    print("4. Peak vs Non-Peak Analysis: Resource allocation optimization")
    print("=" * 80)

if __name__ == "__main__":
    print_kpi_summary()
    main()
