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
        self.assigned_rider = None

class Rider:
    def __init__(self, id, zone, rider_type="fixed"):
        self.id = id
        self.zone = zone
        self.rider_type = rider_type  # "fixed" or "on_demand"
        self.available = True
        self.orders_delivered = 0

class Zone:
    def __init__(self, name):
        self.name = name
        self.customers = []
        self.riders = []
        self.orders = []
        self.unassigned_orders = []