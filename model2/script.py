combined_code = '''
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import time
from datetime import datetime
import pandas as pd
import math

# Core Data and Logic
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

options_map = {
    "a": "BAU",
    "b": "peakday",
    "c": "monthpeak",
    "d": "yearpeak",
    "e": "all"
}

hours_per_day = 16
peak_hours = 8

def calculate_metrics(orders, city_data):
    fixed_riders_used = min(orders // 2, city_data["fixed_riders"])
    adhoc_riders_used = max(0, orders - (fixed_riders_used * 2))
    total_riders = fixed_riders_used + adhoc_riders_used
    OPH = orders / total_riders if total_riders > 0 else 0
    combined_capacity = city_data["fixed_riders"] * 2 + adhoc_riders_used * 1
    combined_utilization = (orders / combined_capacity) * 100 if combined_capacity > 0 else 0
    return {
        'fixed_riders_used': fixed_riders_used,
        'adhoc_riders_used': adhoc_riders_used,
        'total_riders': total_riders,
        'OPH': OPH,
        'combined_utilization': combined_utilization
    }

# GUI Code
class FlipkartSimulationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 Flipkart Quick Commerce - Rider Optimization Simulation")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.running = False
        self.simulation_results = []
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = tk.Label(main_frame, text="🏪 FLIPKART QUICK COMMERCE SIMULATION", 
                              font=("Arial", 18, "bold"), bg='#f0f0f0', fg='#0066cc')
        title_label.pack(pady=(0, 20))
        
        control_frame = ttk.LabelFrame(main_frame, text="🎮 Simulation Controls", padding="15")
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X)
        
        ttk.Label(options_frame, text="Select Simulation Scenario:", 
                 font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        self.option_var = tk.StringVar(value="a")
        
        option_choices = [
            ("🔄 1 day (BAU - Business as Usual)", "a"),
            ("📈 1 day (Peak Day - 22% higher)", "b"),
            ("🚀 1 day (Month Peak - 45% higher)", "c"),
            ("💥 1 day (Year Peak - 200% higher)", "d"),
            ("📊 All Cases (Grand Average)", "e")
        ]
        
        for text, val in option_choices:
            rb = ttk.Radiobutton(options_frame, text=text, variable=self.option_var, value=val)
            rb.pack(anchor=tk.W, pady=3)
        
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.start_button = tk.Button(button_frame, text="🚀 Start Simulation", 
                                     command=self.start_simulation,
                                     bg='#4CAF50', fg='white', font=("Arial", 11, "bold"),
                                     padx=20, pady=10, cursor="hand2")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = tk.Button(button_frame, text="⏹️ Stop Simulation", 
                                    command=self.stop_simulation,
                                    bg='#f44336', fg='white', font=("Arial", 11, "bold"),
                                    padx=20, pady=10, cursor="hand2", state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = tk.Button(button_frame, text="💾 Export Results", 
                                      command=self.export_results,
                                      bg='#2196F3', fg='white', font=("Arial", 11, "bold"),
                                      padx=20, pady=10, cursor="hand2")
        self.export_button.pack(side=tk.LEFT)
        
        self.status_var = tk.StringVar(value="Ready to simulate")
        status_bar = tk.Label(control_frame, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W, bg='white', 
                             font=("Arial", 10))
        status_bar.pack(fill=tk.X, pady=(15, 0))
        
        display_frame = ttk.LabelFrame(main_frame, text="📊 Real-time Simulation Display", padding="15")
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.display_text = ScrolledText(display_frame, 
                                        font=("Consolas", 10),
                                        bg='black', fg='#00ff00',
                                        insertbackground='white',
                                        wrap=tk.NONE,
                                        state=tk.DISABLED)
        self.display_text.pack(fill=tk.BOTH, expand=True)
        
        self.display_text.tag_configure("header", foreground="#ffff00", font=("Consolas", 12, "bold"))
        self.display_text.tag_configure("city", foreground="#ff6600", font=("Consolas", 11, "bold"))
        self.display_text.tag_configure("summary", foreground="#ff0066", font=("Consolas", 10, "bold"))
        self.display_text.tag_configure("data", foreground="#00ffff")
        self.display_text.tag_configure("success", foreground="#00ff00", font=("Consolas", 10, "bold"))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(display_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.log_message("🎉 Welcome to Flipkart Quick Commerce Simulation!", "header")
        self.log_message("📋 Please select a simulation scenario and click 'Start Simulation'", "data")
        self.log_message("⚡ Real-time ticker: 1 hour = 0.125 seconds", "data")
    
    def log_message(self, message, tag="data"):
        def update_display():
            self.display_text.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.display_text.insert(tk.END, f"[{timestamp}] {message}\n", tag)
            self.display_text.see(tk.END)
            self.display_text.config(state=tk.DISABLED)
        
        if threading.current_thread() != threading.main_thread():
            self.root.after(0, update_display)
        else:
            update_display()
    
    def simulate_scenario(self, option):
        scenario_name = options_map[option]
        self.log_message("=" * 80, "header")
        self.log_message(f"🚀 SIMULATION STARTED: {scenario_name.upper()} DAY", "header")
        self.log_message("=" * 80, "header")
        
        total_hours = len(city_metadata) * hours_per_day
        completed_hours = 0
        
        scenario_results = {}
        
        for city in city_metadata:
            if not self.running:
                return None
            
            city_data = city_metadata[city]
            
            self.log_message(f"\n🏙️ PROCESSING CITY: {city.upper()}", "city")
            self.log_message(f"   📊 Fixed Riders: {city_data['fixed_riders']} | Dark Stores: {city_data['dark_stores']} | Traffic Factor: {city_data['traffic_factor']}", "city")
            self.log_message("-" * 80, "data")
            
            hourly_metrics = []
            total_adhoc = 0
            
            for hour in range(1, hours_per_day + 1):
                if not self.running:
                    return None
                
                if hour <= peak_hours:
                    period = "PEAK"
                    order_key = f"{scenario_name}_order_per_hour_peak"
                else:
                    period = "NON-PEAK"
                    order_key = f"{scenario_name}_order_per_hour_non_peak"
                
                orders = city_data[order_key]
                metrics = calculate_metrics(orders, city_data)
                hourly_metrics.append(metrics)
                total_adhoc += metrics['adhoc_riders_used']
                
                self.log_message(f"⏰ Hour {hour:2d} | {period:8} | Orders: {orders:4d} | "
                               f"Fixed: {metrics['fixed_riders_used']:3d} | "
                               f"Adhoc: {metrics['adhoc_riders_used']:3d} | "
                               f"OPH: {metrics['OPH']:5.2f} | "
                               f"Combined Util: {metrics['combined_utilization']:6.2f}%", "data")
                
                completed_hours += 1
                progress = (completed_hours / total_hours) * 100
                self.progress_var.set(progress)
                self.status_var.set(f"Processing {city} - Hour {hour}/{hours_per_day}")

                time.sleep(0.125)
            
            avg_OPH = sum(m['OPH'] for m in hourly_metrics) / len(hourly_metrics)
            avg_adhoc = total_adhoc / len(hourly_metrics) if len(hourly_metrics) > 0 else 0
            avg_combined_util = sum(m['combined_utilization'] for m in hourly_metrics) / len(hourly_metrics)
            
            scenario_results[city] = {
                'avg_OPH': avg_OPH,
                'avg_adhoc': avg_adhoc,
                'avg_combined_util': avg_combined_util
            }
            
            self.log_message("-" * 80, "summary")
            self.log_message(f"📈 CITY SUMMARY - {city.upper()}: Avg OPH = {avg_OPH:.2f} | Avg Combined Utilization = {avg_combined_util:.2f}% | Avg Adhoc Riders = {avg_adhoc:.2f}", "summary")
            self.log_message("-" * 80, "summary")
        
        return scenario_results
    
    def simulate_all_scenarios(self):
        self.log_message("🔄 RUNNING ALL SCENARIOS SIMULATION", "header")
        self.log_message("=" * 80, "header")
        
        all_results = {}
        grand_totals = {"total_OPH": 0, "total_combined_util": 0, "total_adhoc": 0, "count": 0}
        
        for opt in ["a", "b", "c", "d"]:
            if not self.running:
                return
            results = self.simulate_scenario(opt)
            if results:
                all_results[opt] = results
                for city_result in results.values():
                    grand_totals["total_OPH"] += city_result['avg_OPH']
                    grand_totals["total_combined_util"] += city_result['avg_combined_util']
                    grand_totals["total_adhoc"] += city_result['avg_adhoc']
                    grand_totals["count"] += 1
        
        if grand_totals["count"] > 0:
            self.log_message("\n" + "=" * 80, "success")
            self.log_message("🏆 GRAND SUMMARY - ALL SCENARIOS & CITIES", "success")
            self.log_message("=" * 80, "success")
            
            grand_avg_OPH = grand_totals["total_OPH"] / grand_totals["count"]
            grand_avg_combined_util = grand_totals["total_combined_util"] / grand_totals["count"]
            grand_avg_adhoc = grand_totals["total_adhoc"] / grand_totals["count"]
            
            self.log_message(f"📊 Grand Average OPH: {grand_avg_OPH:.2f}", "success")
            self.log_message(f"📊 Grand Average Combined Utilization: {grand_avg_combined_util:.2f}%", "success")
            self.log_message(f"📊 Grand Average Adhoc Riders: {grand_avg_adhoc:.2f}", "success")
            self.log_message("=" * 80, "success")
        
    def start_simulation(self):
        if self.running:
            messagebox.showwarning("Warning", "Simulation is already running!")
            return
        
        self.running = True
        self.simulation_results = []
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        
        self.display_text.config(state=tk.NORMAL)
        self.display_text.delete(1.0, tk.END)
        self.display_text.config(state=tk.DISABLED)
        
        option = self.option_var.get()
        
        def simulation_thread():
            try:
                if option == "e":
                    self.simulate_all_scenarios()
                else:
                    self.simulate_scenario(option)
                
                if self.running:
                    self.log_message("✅ SIMULATION COMPLETED SUCCESSFULLY!", "success")
                    self.status_var.set("Simulation completed successfully")
                    self.progress_var.set(100)
                    
            except Exception as e:
                self.log_message(f"❌ ERROR: {str(e)}", "summary")
                self.status_var.set("Simulation failed")
            finally:
                self.running = False
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
        
        threading.Thread(target=simulation_thread, daemon=True).start()
    
    def stop_simulation(self):
        if self.running:
            self.running = False
            self.log_message("⏹️ SIMULATION STOPPED BY USER", "summary")
            self.status_var.set("Simulation stopped")
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def export_results(self):
        if not self.simulation_results:
            messagebox.showwarning("Warning", "No simulation data to export!")
            return
        
        try:
            df = pd.DataFrame(self.simulation_results)
            filename = f"flipkart_simulation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            
            self.log_message(f"💾 Results exported to: {filename}", "success")
            messagebox.showinfo("Export Successful", f"Results exported to:\n{filename}")
            
        except Exception as e:
            self.log_message(f"❌ Export failed: {str(e)}", "summary")
            messagebox.showerror("Export Failed", f"Failed to export results:\n{str(e)}")
    
    def run(self):
        def on_closing():
            if self.running:
                if messagebox.askokcancel("Quit", "Simulation is running. Do you want to quit?"):
                    self.running = False
                    self.root.after(1000, self.root.destroy)
            else:
                self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    app = FlipkartSimulationGUI()
    app.run()
'''

with open("flipkart_simulation_all_in_one.py", "w") as f:
    f.write(combined_code)