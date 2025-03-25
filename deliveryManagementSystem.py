from typing import List, Optional
from CIACO_Algo import CIACO
from Truck import Truck
from Order import Order
from helper_functions import total_route_distance

# -------------------------------
# Delivery Management & Dynamic Route Optimization System
# -------------------------------

class DeliveryManagementSystem:
    def __init__(self):
        self.trucks: List[Truck] = []
        # In a real system, this could be replaced by a database or live API integration.
        self.ciaco_optimizer = CIACO()

    def add_truck(self, truck: Truck):
        self.trucks.append(truck)

    def track_ongoing_deliveries(self):
        """
        Monitor ongoing trucks and print their current status.
        In production, this would include real-time GPS tracking and status updates.
        """
        for truck in self.trucks:
            print(truck)
            print("Current Route:", truck.route)
            print("Assigned Orders:", truck.assigned_orders)
            print("----")

    def assign_new_order(self, order: Order) -> Optional[Truck]:
        """
        Assign a new order to an ongoing truck if feasible.
        Checks capacity and route feasibility.
        :param order: The new Order to be assigned.
        :return: The Truck to which the order is assigned, or None if no feasible truck is found.
        """
        candidate_trucks = []
        for truck in self.trucks:
            # Check capacity
            if truck.remaining_capacity >= order.weight:
                candidate_trucks.append(truck)

        if not candidate_trucks:
            print(f"No truck with sufficient capacity for {order}")
            return None

        # For each candidate truck, try to dynamically re-optimize the route
        for truck in candidate_trucks:
            print(f"Evaluating truck {truck.truck_id} for {order}")
            # Create a new set of stops: current route stops + pickup and dropoff of new order.
            # We assume the route is a list of stops (coordinates) that includes the current position and already assigned deliveries.
            new_stops = truck.route.copy()
            # To keep things generic, add the new pickup and drop-off.
            # In a real implementation, the pickup should be inserted before dropoff.
            new_stops.extend([order.pickup, order.dropoff])
            # Remove duplicates if necessary
            new_stops = list(dict.fromkeys(new_stops))

            # Use the CIACO optimizer to compute an updated route.
            optimized_route = self.ciaco_optimizer.optimize_route(new_stops)
            # Check route feasibility: Here we simply compare the new route distance with a threshold.
            # In a real system, additional checks such as time window constraints would be applied.
            current_distance = total_route_distance(truck.route)
            new_distance = total_route_distance(optimized_route)
            print(f"Truck {truck.truck_id}: current distance = {current_distance:.2f}, new distance = {new_distance:.2f}")

            # For demonstration, we require that the new route does not exceed the current route by more than 20%
            if new_distance <= current_distance * 1.2 or current_distance == 0:
                # Accept the new route and assign the order.
                truck.add_order(order)
                truck.route = optimized_route
                print(f"Order {order.order_id} assigned to Truck {truck.truck_id}. Updated route: {truck.route}")
                return truck
            else:
                print(f"Truck {truck.truck_id}: New route not feasible for additional order {order.order_id}")

        print(f"Order {order.order_id} could not be assigned to any truck.")
        return None