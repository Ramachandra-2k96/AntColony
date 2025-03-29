import folium
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import random
from typing import List, Tuple, Dict
import osmnx as ox
import networkx as nx
from CIACO_Algo import CIACO
from Truck import Truck
from Order import Order

class ACOVisualization:
    def __init__(self, location_data=None):
        """
        Initialize the ACO visualization with location data if provided
        
        Args:
            location_data: Pandas DataFrame with columns ['id', 'x', 'y'] or None
        """
        self.location_data = location_data
        self.ciaco = CIACO(num_ants=15, iterations=50, alpha=1.0, beta=2.0)
        self.network_graph = None
        self.trucks = {}
        self.orders = {}
        self.node_mapping = {}  # Maps (lat, lon) to network node
        
    def load_data_from_csv(self, filename):
        """
        Load location data from a CSV file
        
        Args:
            filename: Path to the CSV file
        """
        self.location_data = pd.read_csv(filename)
        
        # Ensure the dataframe has the required columns
        if 'id' not in self.location_data.columns:
            self.location_data = self.location_data.reset_index().rename(columns={"index": "id"})
        
        # Rename latitude/longitude columns if necessary
        if 'Latitude' in self.location_data.columns and 'y' not in self.location_data.columns:
            self.location_data = self.location_data.rename(columns={"Latitude": "y", "Longitude": "x"})
            
        print(f"Loaded {len(self.location_data)} locations")
        return self.location_data
    
    def create_street_network(self, center_point=None, distance=25000):
        """
        Create a street network around a center point
        
        Args:
            center_point: (y, x) tuple representing the center point
            distance: Distance in meters to create the network around
        """
        if center_point is None and self.location_data is not None and len(self.location_data) > 0:
            # Use the first point as the center
            center_point = (self.location_data.iloc[0]['y'], self.location_data.iloc[0]['x'])
        
        if center_point is None:
            raise ValueError("No center point provided and no location data available")
            
        print(f"Creating street network around {center_point} with {distance}m radius")
        self.network_graph = ox.graph_from_point(center_point, dist=distance, network_type="drive")
        self.network_graph = ox.add_edge_speeds(self.network_graph)
        self.network_graph = ox.add_edge_travel_times(self.network_graph)
        
        # Map all locations to network nodes
        if self.location_data is not None:
            self._map_locations_to_nodes()
            
        return self.network_graph
    
    def _map_locations_to_nodes(self):
        """Map all locations to their nearest network nodes"""
        if self.network_graph is None:
            raise ValueError("No network graph created. Call create_street_network first.")
            
        print("Mapping locations to network nodes...")
        
        # For each point in location_data, find the nearest node
        for _, row in self.location_data.iterrows():
            point = (row['y'], row['x'])
            nearest_node = ox.distance.nearest_nodes(self.network_graph, row['x'], row['y'])
            self.node_mapping[point] = nearest_node
            
        print(f"Mapped {len(self.node_mapping)} locations to network nodes")
    
    def plot_network(self, figsize=(12, 8)):
        """
        Plot the street network
        
        Args:
            figsize: Figure size as (width, height) tuple
        """
        if self.network_graph is None:
            raise ValueError("No network graph created. Call create_street_network first.")
            
        fig, ax = ox.plot_graph(self.network_graph, bgcolor="lightgray", 
                               node_size=10, node_color="purple", 
                               figsize=figsize)
        return fig, ax
    
    def create_trucks(self, num_trucks=3, max_capacity=1000, start_location=None):
        """
        Create a number of trucks with random or specified starting locations
        
        Args:
            num_trucks: Number of trucks to create
            max_capacity: Maximum capacity of each truck
            start_location: Starting location for all trucks or None for random locations
        """
        self.trucks = {}
        
        if start_location is None and self.location_data is not None:
            # Use random points from the location data as starting points
            start_indices = random.sample(range(len(self.location_data)), min(num_trucks, len(self.location_data)))
            for i, idx in enumerate(start_indices):
                truck_id = f"T{i+1}"
                location = (self.location_data.iloc[idx]['y'], self.location_data.iloc[idx]['x'])
                capacity = random.randint(max_capacity//2, max_capacity)
                self.trucks[truck_id] = Truck(truck_id, location, capacity)
        else:
            # Use the provided start location or the first location in the data
            if start_location is None and self.location_data is not None:
                start_location = (self.location_data.iloc[0]['y'], self.location_data.iloc[0]['x'])
            
            if start_location is None:
                raise ValueError("No start location provided and no location data available")
                
            for i in range(num_trucks):
                truck_id = f"T{i+1}"
                capacity = random.randint(max_capacity//2, max_capacity)
                self.trucks[truck_id] = Truck(truck_id, start_location, capacity)
                
        return self.trucks
    
    def create_orders(self, num_orders=10, max_weight=500):
        """
        Create random orders using points from the location data
        
        Args:
            num_orders: Number of orders to create
            max_weight: Maximum weight of each order
        """
        if self.location_data is None or len(self.location_data) < 2:
            raise ValueError("Not enough location data to create orders")
            
        self.orders = {}
        
        for i in range(num_orders):
            # Select random pickup and dropoff locations
            pickup_idx, dropoff_idx = random.sample(range(len(self.location_data)), 2)
            
            order_id = f"O{i+1}"
            pickup = (self.location_data.iloc[pickup_idx]['y'], self.location_data.iloc[pickup_idx]['x'])
            dropoff = (self.location_data.iloc[dropoff_idx]['y'], self.location_data.iloc[dropoff_idx]['x'])
            weight = random.randint(max_weight//10, max_weight)
            
            self.orders[order_id] = Order(order_id, weight, pickup, dropoff)
            
        return self.orders
    
    def assign_orders_to_trucks(self, strategy="greedy"):
        """
        Assign orders to trucks using various strategies
        
        Args:
            strategy: Assignment strategy ('greedy', 'balanced', 'nearest')
        """
        if not self.trucks:
            raise ValueError("No trucks created. Call create_trucks first.")
        if not self.orders:
            raise ValueError("No orders created. Call create_orders first.")
            
        # Reset truck assignments
        for truck in self.trucks.values():
            truck.assigned_orders = []
            truck.update_capacity()
            
        if strategy == "greedy":
            # Assign each order to the truck with the most remaining capacity
            for order_id, order in self.orders.items():
                best_truck = None
                best_capacity = -1
                
                for truck_id, truck in self.trucks.items():
                    if truck.remaining_capacity >= order.weight and truck.remaining_capacity > best_capacity:
                        best_truck = truck
                        best_capacity = truck.remaining_capacity
                
                if best_truck:
                    best_truck.add_order(order)
        
        elif strategy == "balanced":
            # Sort orders by weight (heaviest first)
            sorted_orders = sorted(self.orders.items(), key=lambda x: x[1].weight, reverse=True)
            
            # Sort trucks by capacity (largest first)
            sorted_trucks = sorted(self.trucks.items(), key=lambda x: x[1].max_capacity, reverse=True)
            
            # Assign orders round-robin to balance load
            for i, (order_id, order) in enumerate(sorted_orders):
                assigned = False
                
                # Try each truck in rotation
                for j in range(len(sorted_trucks)):
                    truck_idx = (i + j) % len(sorted_trucks)
                    truck = sorted_trucks[truck_idx][1]
                    
                    if truck.remaining_capacity >= order.weight:
                        truck.add_order(order)
                        assigned = True
                        break
                
                if not assigned:
                    print(f"Could not assign order {order_id} (weight {order.weight}) to any truck")
        
        elif strategy == "nearest":
            # Assign each order to the nearest truck that has capacity
            for order_id, order in self.orders.items():
                best_truck = None
                best_distance = float('inf')
                
                for truck_id, truck in self.trucks.items():
                    if truck.remaining_capacity >= order.weight:
                        # Calculate distance from truck to pickup
                        distance = self._calculate_distance(truck.current_location, order.pickup)
                        
                        if distance < best_distance:
                            best_truck = truck
                            best_distance = distance
                
                if best_truck:
                    best_truck.add_order(order)
                else:
                    print(f"Could not assign order {order_id} (weight {order.weight}) to any truck")
        
        # Print assignment summary
        for truck_id, truck in self.trucks.items():
            total_weight = sum(order.weight for order in truck.assigned_orders)
            print(f"Truck {truck_id}: {len(truck.assigned_orders)} orders, {total_weight}/{truck.max_capacity} capacity used")
            
    def _calculate_distance(self, point1, point2):
        """
        Calculate Euclidean distance between two points
        
        Args:
            point1: (y, x) tuple for first point
            point2: (y, x) tuple for second point
        """
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def optimize_routes(self):
        """
        Optimize routes for each truck using the CIACO algorithm
        """
        if not self.trucks:
            raise ValueError("No trucks created. Call create_trucks first.")
            
        for truck_id, truck in self.trucks.items():
            if not truck.assigned_orders:
                print(f"Truck {truck_id} has no assigned orders, skipping route optimization")
                continue
                
            # Create a list of stops: start with current location, then pickups, then dropoffs
            stops = [truck.current_location]
            
            # Add all pickups first
            for order in truck.assigned_orders:
                stops.append(order.pickup)
                
            # Then add all dropoffs
            for order in truck.assigned_orders:
                stops.append(order.dropoff)
                
            # Optimize route with CIACO
            print(f"Optimizing route for truck {truck_id} with {len(stops)} stops")
            try:
                optimized_route = self.ciaco.optimize_route(stops)
                truck.route = optimized_route
                print(f"Route optimized with {len(optimized_route)} stops")
            except Exception as e:
                print(f"Error optimizing route for truck {truck_id}: {e}")
                truck.route = stops
    
    def _get_node_for_point(self, point):
        """
        Get the nearest network node for a point, adding it to the mapping if not already present
        
        Args:
            point: (y, x) tuple
        
        Returns:
            The nearest node ID in the network
        """
        if point in self.node_mapping:
            return self.node_mapping[point]
            
        if self.network_graph is None:
            raise ValueError("No network graph created. Call create_street_network first.")
            
        # Find the nearest node
        nearest_node = ox.distance.nearest_nodes(self.network_graph, point[1], point[0])
        self.node_mapping[point] = nearest_node
        return nearest_node
    
    def _get_road_path_between_points(self, point1, point2):
        """
        Get the actual road path between two points using the network graph
        
        Args:
            point1: (y, x) tuple for first point
            point2: (y, x) tuple for second point
            
        Returns:
            List of (y, x) coordinates representing the path along the road network
        """
        if self.network_graph is None:
            raise ValueError("No network graph created. Call create_street_network first.")
            
        # Get nodes for the points
        node1 = self._get_node_for_point(point1)
        node2 = self._get_node_for_point(point2)
        
        try:
            # Get the shortest path between the nodes
            path = nx.shortest_path(self.network_graph, source=node1, target=node2, weight='travel_time')
            
            # Extract the coordinates for each node in the path
            coords = []
            for node in path:
                y = self.network_graph.nodes[node]['y']
                x = self.network_graph.nodes[node]['x']
                coords.append((y, x))
                
            return coords
        except Exception as e:
            print(f"Error finding path between {point1} and {point2}: {e}")
            # If there's an error, return just the endpoints
            return [point1, point2]
                
    def visualize_on_map(self, center=None, use_road_network=True):
        """
        Create an interactive map with trucks, orders, and routes
        
        Args:
            center: (y, x) tuple for map center or None to auto-center
            use_road_network: Whether to use the actual road network for paths (True) or direct lines (False)
        """
        if not self.trucks and not self.orders:
            raise ValueError("No trucks or orders created")
            
        # If using road network and no network graph exists, create one
        if use_road_network and self.network_graph is None:
            print("Using road network but no network graph exists, creating one...")
            if center is not None:
                self.create_street_network(center_point=center)
            elif self.location_data is not None and len(self.location_data) > 0:
                self.create_street_network()
            else:
                # Try to use truck location as center
                if self.trucks:
                    truck = next(iter(self.trucks.values()))
                    self.create_street_network(center_point=truck.current_location)
                else:
                    raise ValueError("Cannot create network graph: no center point provided and no location data")
            
        # Determine map center
        if center is None:
            if self.location_data is not None and len(self.location_data) > 0:
                center = (self.location_data['y'].mean(), self.location_data['x'].mean())
            elif self.trucks:
                # Use the first truck's location
                center = next(iter(self.trucks.values())).current_location
            elif self.orders:
                # Use the first order's pickup location
                center = next(iter(self.orders.values())).pickup
            else:
                center = (0, 0)
                
        # Create map
        map_obj = folium.Map(location=center, tiles="cartodbpositron", zoom_start=12)
        
        # Add trucks to map
        for truck_id, truck in self.trucks.items():
            # Create a popup with truck info
            popup_text = f"""
            <b>Truck {truck_id}</b><br>
            Capacity: {truck.remaining_capacity}/{truck.max_capacity}<br>
            Orders: {len(truck.assigned_orders)}
            """
            
            # Add truck marker
            folium.Marker(
                location=truck.current_location,
                popup=popup_text,
                icon=folium.Icon(color='green', icon='truck', prefix='fa')
            ).add_to(map_obj)
            
            # Add route if it exists
            if hasattr(truck, 'route') and len(truck.route) > 1:
                # Generate a color for this truck's route
                color = f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}"
                
                if use_road_network:
                    # Add each segment of the route using road network
                    for i in range(len(truck.route) - 1):
                        start_point = truck.route[i]
                        end_point = truck.route[i + 1]
                        
                        # Get the actual road path between the points
                        path_coords = self._get_road_path_between_points(start_point, end_point)
                        
                        # Add the path segment to the map
                        folium.PolyLine(
                            locations=path_coords,
                            color=color,
                            weight=4,
                            opacity=0.7,
                            popup=f"Truck {truck_id} route segment {i+1}"
                        ).add_to(map_obj)
                else:
                    # Add direct route as a PolyLine (original behavior)
                    folium.PolyLine(
                        locations=truck.route,
                        color=color,
                        weight=4,
                        opacity=0.7,
                        popup=f"Truck {truck_id} route"
                    ).add_to(map_obj)
                
                # Add markers for each stop with order info
                for i, stop in enumerate(truck.route):
                    if i == 0:
                        # Skip start point (already marked as truck)
                        continue
                        
                    # Determine if this is a pickup or dropoff
                    is_pickup = any(order.pickup == stop for order in truck.assigned_orders)
                    is_dropoff = any(order.dropoff == stop for order in truck.assigned_orders)
                    
                    if is_pickup:
                        icon_color = 'blue'
                        icon_name = 'arrow-up'
                        stop_type = 'Pickup'
                    elif is_dropoff:
                        icon_color = 'red'
                        icon_name = 'arrow-down'
                        stop_type = 'Dropoff'
                    else:
                        icon_color = 'gray'
                        icon_name = 'circle'
                        stop_type = 'Stop'
                    
                    # Find the order for this stop
                    order_info = ""
                    for order in truck.assigned_orders:
                        if order.pickup == stop or order.dropoff == stop:
                            order_info = f"<br>Order: {order.order_id}<br>Weight: {order.weight}"
                            break
                    
                    # Add marker
                    folium.Marker(
                        location=stop,
                        popup=f"{stop_type} {i}{order_info}",
                        icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
                    ).add_to(map_obj)
        
        # Add unassigned orders to map
        assigned_orders = set()
        for truck in self.trucks.values():
            for order in truck.assigned_orders:
                assigned_orders.add(order.order_id)
        
        for order_id, order in self.orders.items():
            if order_id not in assigned_orders:
                # Add pickup marker
                folium.Marker(
                    location=order.pickup,
                    popup=f"Unassigned Pickup: {order_id}<br>Weight: {order.weight}",
                    icon=folium.Icon(color='orange', icon='arrow-up', prefix='fa')
                ).add_to(map_obj)
                
                # Add dropoff marker
                folium.Marker(
                    location=order.dropoff,
                    popup=f"Unassigned Dropoff: {order_id}<br>Weight: {order.weight}",
                    icon=folium.Icon(color='orange', icon='arrow-down', prefix='fa')
                ).add_to(map_obj)
                
        return map_obj
    
    def visualize_capacity_timeline(self, figsize=(12, 6)):
        """
        Visualize the truck capacity timeline as routes are followed
        """
        if not self.trucks:
            raise ValueError("No trucks created. Call create_trucks first.")
            
        # Count number of trucks with routes
        trucks_with_routes = sum(1 for truck in self.trucks.values() if hasattr(truck, 'route') and len(truck.route) > 1)
        
        if trucks_with_routes == 0:
            raise ValueError("No trucks have routes. Call optimize_routes first.")
            
        # Create figure
        fig, axes = plt.subplots(trucks_with_routes, 1, figsize=figsize, sharex=True)
        
        # If only one truck has a route, wrap axes in a list
        if trucks_with_routes == 1:
            axes = [axes]
            
        # Track which axis we're on
        ax_index = 0
        
        # Plot each truck's capacity timeline
        for truck_id, truck in self.trucks.items():
            if not hasattr(truck, 'route') or len(truck.route) <= 1:
                continue
                
            ax = axes[ax_index]
            ax_index += 1
            
            # Initialize capacity at starting value
            current_capacity = truck.max_capacity
            capacities = [current_capacity]
            labels = ["Start"]
            positions = [0]
            
            # Track order pickup/dropoff status
            order_status = {order.order_id: {"picked_up": False} for order in truck.assigned_orders}
            
            # Simulate route traversal
            for i, stop in enumerate(truck.route[1:], 1):  # Skip first stop (starting point)
                # Check if this stop is a pickup or dropoff
                for order in truck.assigned_orders:
                    # If it's a pickup and not already picked up
                    if stop == order.pickup and not order_status[order.order_id]["picked_up"]:
                        current_capacity -= order.weight
                        capacities.append(current_capacity)
                        labels.append(f"Pickup {order.order_id}")
                        positions.append(i)
                        order_status[order.order_id]["picked_up"] = True
                        break
                        
                    # If it's a dropoff and already picked up
                    elif stop == order.dropoff and order_status[order.order_id]["picked_up"]:
                        current_capacity += order.weight
                        capacities.append(current_capacity)
                        labels.append(f"Dropoff {order.order_id}")
                        positions.append(i)
                        break
            
            # Plot capacity timeline
            ax.step(positions, capacities, where='post', linewidth=2, 
                    color=f"#{random.randint(0, 200):02x}{random.randint(0, 200):02x}{random.randint(0, 200):02x}")
            
            # Add markers for each stop
            for pos, cap, label in zip(positions, capacities, labels):
                ax.plot(pos, cap, 'o', markersize=8)
                ax.text(pos, cap + (truck.max_capacity * 0.03), label, rotation=45, ha='right')
                
            # Set axis labels
            ax.set_ylabel("Capacity")
            ax.set_title(f"Truck {truck_id} Capacity Timeline")
            
            # Set y-axis limits
            ax.set_ylim(0, truck.max_capacity * 1.1)
            
            # Add a horizontal line for max capacity
            ax.axhline(y=truck.max_capacity, color='r', linestyle='--', alpha=0.5)
            ax.text(0, truck.max_capacity * 1.02, f"Max Capacity: {truck.max_capacity}", color='r')
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
        # Set common x-axis label
        fig.text(0.5, 0.04, "Stop Number", ha='center')
        
        # Adjust layout
        plt.tight_layout()
        return fig, axes
        
# Create a demo function to show the visualization in action
def demo_visualization(use_road_network=True):
    # Create sample data
    locations = pd.DataFrame({
        'id': range(20),
        'x': np.random.uniform(77.5, 77.7, 20),  # Bangalore longitudes
        'y': np.random.uniform(12.9, 13.1, 20),  # Bangalore latitudes
    })
    
    # Create visualization
    vis = ACOVisualization(locations)
    
    # Create the street network
    if use_road_network:
        center_point = (locations['y'].mean(), locations['x'].mean())
        vis.create_street_network(center_point=center_point, distance=10000)
    
    # Create trucks and orders
    vis.create_trucks(num_trucks=3, max_capacity=1000)
    vis.create_orders(num_orders=8, max_weight=300)
    
    # Assign orders and optimize routes
    vis.assign_orders_to_trucks(strategy="balanced")
    vis.optimize_routes()
    
    # Create visualizations
    map_obj = vis.visualize_on_map(use_road_network=use_road_network)
    capacity_fig, _ = vis.visualize_capacity_timeline()
    
    # Display map
    return map_obj, capacity_fig

if __name__ == "__main__":
    # Run the demo
    print("Creating visualization with actual road network paths...")
    map_obj, capacity_fig = demo_visualization(use_road_network=True)
    
    # Save the map to an HTML file
    map_obj.save("aco_route_map.html")
    
    # Display the capacity timeline
    plt.savefig("capacity_timeline.png", dpi=300, bbox_inches="tight")
    plt.show()
    
    print("Visualization complete! Check aco_route_map.html and capacity_timeline.png") 