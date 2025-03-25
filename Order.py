from typing import Tuple

class Order:
    def __init__(self, order_id: str, weight: float, pickup: Tuple[float, float],
                 dropoff: Tuple[float, float]):
        """
        Represents a delivery order.
        :param order_id: Unique identifier for the order.
        :param weight: Weight (or capacity requirement) of the order.
        :param pickup: Coordinates (x, y) for pickup location.
        :param dropoff: Coordinates (x, y) for drop-off location.
        """
        self.order_id = order_id
        self.weight = weight
        self.pickup = pickup
        self.dropoff = dropoff

    def __repr__(self):
        return f"Order({self.order_id}, {self.weight}kg)"