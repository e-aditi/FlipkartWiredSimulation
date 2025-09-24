
import math

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
    # Combined Utilization (%) = orders / (fixed_riders * 2 + adhoc_riders * 1) * 100
    combined_capacity = city_data["fixed_riders"] * 2 + adhoc_riders_used * 1
    combined_utilization = (orders / combined_capacity) * 100 if combined_capacity > 0 else 0
    return {
        'fixed_riders_used': fixed_riders_used,
        'adhoc_riders_used': adhoc_riders_used,
        'total_riders': total_riders,
        'OPH': OPH,
        'combined_utilization': combined_utilization
    }
