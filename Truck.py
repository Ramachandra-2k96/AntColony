from typing import List, Tuple
from Order import Order

class Truck:
    def __init__(self, truck_id: str, current_location: Tuple[float, float],
                 max_capacity: float):
        """
        Represents an ongoing truck with its current delivery route and capacity.
        :param truck_id: Unique identifier for the truck.
        :param current_location: The current (x, y) location of the truck.
        :param max_capacity: Maximum load capacity of the truck.
        """
        self.truck_id = truck_id
        self.current_location = current_location
        self.max_capacity = max_capacity
        # List of orders (each order includes pickup and dropoff stops)
        self.assigned_orders: List[Order] = []
        # For simplicity, maintain a route as a list of stops (each stop is a tuple (x, y))
        # Initial route starts at the truck's current location (assume depot is its starting point)
        self.route: List[Tuple[float, float]] = [current_location]
        # Track remaining capacity
        self.remaining_capacity = max_capacity

    def update_capacity(self):
        """
        Update remaining capacity based on the assigned orders.
        """
        used_capacity = sum(order.weight for order in self.assigned_orders)
        self.remaining_capacity = self.max_capacity - used_capacity

    def add_order(self, order: Order):
        """
        Add a new order to the truck and update route and capacity.
        """
        self.assigned_orders.append(order)
        self.update_capacity()

    def __repr__(self):
        return f"Truck({self.truck_id}, remaining_capacity={self.remaining_capacity}kg)"