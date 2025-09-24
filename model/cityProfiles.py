
dark_store_radius_km = 3
dark_store_area = 3.14 * (dark_store_radius_km ** 2)

city_metadata = {
    "Delhi": {
        "avg_zone_size": dark_store_area,
        "base_delivery_time": 8,
        #super density zone area of Delhi in sq Km. >20,000 people/sq km
        "area_sq_km": 141,
        "total_riders": 75
    },
    "Pune": {
        "avg_zone_size": dark_store_area,
        "base_delivery_time": 10,
        #super density zone area of Pune in sq Km. >20,000 people/sq km
        "area_sq_km": 10,
        "total_riders": 30,
    }
}
