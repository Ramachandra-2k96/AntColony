import folium
import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional
from CIACO_Algo import CIACO
from datetime import datetime, timedelta
import json
import h3.api.basic_int as h3
from GIS import hexMerge

class DynamicRoutingSystem:
    def __init__(self):
        self.trucks: Dict[str, Dict] = {}  # truck_id -> {current_location, capacity, current_route, deliveries}
        self.deliveries: Dict[str, Dict] = {}  # delivery_id -> {pickup, dropoff, weight, status, time_window}
        self.map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Centered on India
        self.ciaco = CIACO(num_ants=10, iterations=50)
        self.H3_RESOLUTION = 8
        self.hex_counts = None
        self.truck_data = None
        
    def load_truck_data(self, excel_file: str):
        """Load truck data from Excel file and create hexagonal grid"""
        # Read truck data
        self.truck_data = pd.read_excel(excel_file)
        
        # Clean and validate data
        self.truck_data["Latitude"] = self.truck_data["Latitude"].astype(float)
        self.truck_data["Longitude"] = self.truck_data["Longitude"].astype(float)
        
        # Remove invalid rows
        self.truck_data = self.truck_data.dropna(subset=["Latitude", "Longitude"])
        self.truck_data = self.truck_data[
            (self.truck_data["Latitude"].between(-90, 90)) & 
            (self.truck_data["Longitude"].between(-180, 180))
        ]
        
        # Assign hexagons
        self.truck_data["hex_id"] = self.truck_data.apply(
            lambda row: h3.latlng_to_cell(row["Latitude"], row["Longitude"], self.H3_RESOLUTION), 
            axis=1
        )
        
        # Count trucks per hexagon
        self.hex_counts = self.truck_data["hex_id"].value_counts().reset_index()
        self.hex_counts.columns = ["hex_id", "truck_count"]
        
        # Merge low-density hexagons
        K_MIN = 10
        self.hex_counts, merged_hexes = hexMerge.merge_hexagons(self.hex_counts, K_MIN)
        
        # Subdivide high-density hexagons
        MAX_TRUCKS = 50
        high_density_hexes = self.hex_counts[self.hex_counts["truck_count"] >= K_MIN]
        high_density_hexes["sub_hexes"] = high_density_hexes.apply(
            lambda row: h3.cell_to_children(row["hex_id"], self.H3_RESOLUTION + 1) 
            if row["truck_count"] > MAX_TRUCKS else [row["hex_id"]], 
            axis=1
        )
        
        # Expand subdivided hexagons
        sub_hex_list = high_density_hexes.explode("sub_hexes")[["sub_hexes", "truck_count"]]
        sub_hex_list.columns = ["hex_id", "truck_count"]
        
        # Combine all hexagons
        self.hex_counts = pd.concat([self.hex_counts, sub_hex_list])
        
    def add_truck(self, truck_id: str, max_capacity: float, current_location: Tuple[float, float]):
        """Add a new truck to the system"""
        self.trucks[truck_id] = {
            'max_capacity': max_capacity,
            'current_capacity': max_capacity,
            'current_location': current_location,
            'current_route': [],
            'deliveries': [],
            'last_update': datetime.now(),
            'hex_id': h3.latlng_to_cell(current_location[0], current_location[1], self.H3_RESOLUTION),
            'total_weight': 0  # Track total weight of all deliveries
        }
        
    def add_delivery(self, delivery_id: str, pickup: Tuple[float, float], 
                    dropoff: Tuple[float, float], weight: float,
                    time_window: Optional[Tuple[datetime, datetime]] = None):
        """Add a new delivery request"""
        self.deliveries[delivery_id] = {
            'pickup': pickup,
            'dropoff': dropoff,
            'weight': weight,
            'status': 'pending',
            'assigned_truck': None,
            'pickup_hex': h3.latlng_to_cell(pickup[0], pickup[1], self.H3_RESOLUTION),
            'dropoff_hex': h3.latlng_to_cell(dropoff[0], dropoff[1], self.H3_RESOLUTION),
            'time_window': time_window
        }
        
    def find_suitable_truck(self, delivery_id: str) -> Optional[str]:
        """Find a suitable truck for a delivery based on capacity and location"""
        delivery = self.deliveries[delivery_id]
        best_truck = None
        min_distance = float('inf')
        
        for truck_id, truck in self.trucks.items():
            # Check total weight constraint first
            if truck['total_weight'] + delivery['weight'] > truck['max_capacity']:
                continue
                
            # Check current capacity
            if truck['current_capacity'] >= delivery['weight']:
                # Check time window if specified
                if delivery['time_window']:
                    start_time, end_time = delivery['time_window']
                    if not self._can_meet_time_window(truck_id, delivery, start_time, end_time):
                        continue
                
                # Calculate distance from truck's current location to pickup
                distance = self._calculate_distance(truck['current_location'], delivery['pickup'])
                if distance < min_distance:
                    min_distance = distance
                    best_truck = truck_id
                    
        return best_truck
    
    def _can_meet_time_window(self, truck_id: str, delivery: Dict, 
                            start_time: datetime, end_time: datetime) -> bool:
        """Check if truck can meet delivery time window"""
        truck = self.trucks[truck_id]
        current_time = datetime.now()
        
        # If current time is past the end time, return False
        if current_time > end_time:
            return False
            
        # Use the start time if current time is before start time
        effective_start = max(current_time, start_time)
        
        # Calculate estimated time to pickup with faster speed assumption
        distance_to_pickup = self._calculate_distance(truck['current_location'], delivery['pickup'])
        # Use 80km/h for faster delivery estimation (being more lenient)
        estimated_time_to_pickup = effective_start + timedelta(hours=distance_to_pickup/80)
        
        # Calculate estimated time to dropoff with faster speed
        distance_to_dropoff = self._calculate_distance(delivery['pickup'], delivery['dropoff'])
        estimated_time_to_dropoff = estimated_time_to_pickup + timedelta(hours=distance_to_dropoff/80)
        
        # Add smaller buffer time for loading/unloading
        estimated_time_to_dropoff += timedelta(minutes=15)
        
        # Being more lenient with time windows - only check if we can start the delivery
        # within the time window, not necessarily complete it
        return estimated_time_to_pickup <= end_time
    
    def optimize_route(self, truck_id: str, new_delivery_id: str) -> List[Tuple[float, float]]:
        """Optimize route for a truck including a new delivery"""
        truck = self.trucks[truck_id]
        new_delivery = self.deliveries[new_delivery_id]
        
        # Create list of all stops including new delivery
        stops = [truck['current_location']]  # Start from current location
        
        # Add existing delivery stops
        for delivery_id in truck['deliveries']:
            delivery = self.deliveries[delivery_id]
            if delivery['status'] == 'in_progress':
                stops.append(delivery['dropoff'])
                
        # Add new delivery stops
        stops.append(new_delivery['pickup'])
        stops.append(new_delivery['dropoff'])
        
        # Optimize route using CIACO
        optimized_route = self.ciaco.optimize_route(stops)
        return optimized_route
    
    def update_truck_status(self, truck_id: str, new_location: Tuple[float, float]):
        """Update truck's current location and status"""
        truck = self.trucks[truck_id]
        truck['current_location'] = new_location
        truck['last_update'] = datetime.now()
        truck['hex_id'] = h3.latlng_to_cell(new_location[0], new_location[1], self.H3_RESOLUTION)
        
        # Update delivery statuses
        for delivery_id in truck['deliveries']:
            delivery = self.deliveries[delivery_id]
            if delivery['status'] == 'in_progress':
                # Check if truck has reached delivery point
                if self._calculate_distance(new_location, delivery['dropoff']) < 0.01:  # 10 meters threshold
                    delivery['status'] = 'completed'
                    truck['current_capacity'] += delivery['weight']
                    truck['total_weight'] -= delivery['weight']
                    truck['deliveries'].remove(delivery_id)
    
    def visualize_routes(self):
        """Visualize all truck routes on the map with hexagonal grid"""
        # Clear existing map
        self.map = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
        
        # Plot hexagonal grid
        if self.hex_counts is not None:
            for _, row in self.hex_counts.iterrows():
                hex_id = row["hex_id"]
                boundary = h3.cell_to_boundary(hex_id)
                folium.Polygon(
                    locations=boundary,
                    color='blue' if row["truck_count"] < 20 else 'red',
                    weight=2,
                    fill=True,
                    fill_color='blue' if row["truck_count"] < 20 else 'red',
                    fill_opacity=0.6,
                    popup=f"Trucks in area: {row['truck_count']}"
                ).add_to(self.map)
        
        # Plot truck locations and routes
        for truck_id, truck in self.trucks.items():
            # Plot truck location
            folium.Marker(
                location=truck['current_location'],
                popup=f"Truck {truck_id}<br>Capacity: {truck['current_capacity']}/{truck['max_capacity']}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(self.map)
            
            # Plot route if exists
            if truck['current_route']:
                folium.PolyLine(
                    locations=truck['current_route'],
                    weight=2,
                    color='green',
                    opacity=0.8
                ).add_to(self.map)
                
            # Plot delivery points
            for delivery_id in truck['deliveries']:
                delivery = self.deliveries[delivery_id]
                folium.Marker(
                    location=delivery['pickup'],
                    popup=f"Pickup {delivery_id}",
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(self.map)
                folium.Marker(
                    location=delivery['dropoff'],
                    popup=f"Dropoff {delivery_id}",
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(self.map)
        
        # Save map
        self.map.save("dynamic_routes.html")
        
    def _calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def assign_delivery(self, delivery_id: str) -> bool:
        """Assign a delivery to a suitable truck"""
        if delivery_id not in self.deliveries:
            return False
            
        delivery = self.deliveries[delivery_id]
        if delivery['status'] != 'pending':
            return False
            
        # Find suitable truck
        truck_id = self.find_suitable_truck(delivery_id)
        if not truck_id:
            return False
            
        # Assign delivery to truck
        truck = self.trucks[truck_id]
        delivery['status'] = 'in_progress'
        delivery['assigned_truck'] = truck_id
        truck['deliveries'].append(delivery_id)
        truck['total_weight'] += delivery['weight']
        truck['current_capacity'] -= delivery['weight']
        
        # Update route for truck
        truck['current_route'] = self.optimize_route(truck_id, delivery_id)
        
        return True
    
    def handle_truck_breakdown(self, truck_id: str) -> bool:
        """Handle truck breakdown by reassigning deliveries to other trucks"""
        if truck_id not in self.trucks:
            return False
            
        # Get all deliveries from the broken truck
        failed_deliveries = list(self.trucks[truck_id]['deliveries'].copy())
        failed_delivery_objects = []
        
        # Collect all delivery objects and their weights before removing the truck
        for delivery_id in failed_deliveries:
            delivery = self.deliveries[delivery_id]
            failed_delivery_objects.append({
                'id': delivery_id,
                'weight': delivery['weight'],
                'status': delivery['status']
            })
            # Reset delivery status
            delivery['status'] = 'pending'
            delivery['assigned_truck'] = None
        
        # Remove the broken truck
        del self.trucks[truck_id]
        
        # Sort deliveries by weight (descending) to handle larger deliveries first
        failed_delivery_objects.sort(key=lambda x: x['weight'], reverse=True)
        
        # Try to reassign each delivery
        success = True
        for delivery_obj in failed_delivery_objects:
            delivery_id = delivery_obj['id']
            
            # Try to find a new truck with priority
            new_truck_id = None
            min_distance = float('inf')
            
            # First pass - try to find trucks with enough capacity
            for tid, truck in self.trucks.items():
                delivery = self.deliveries[delivery_id]
                # More lenient capacity check
                if truck['current_capacity'] >= delivery['weight'] * 0.9:  # Allow 10% overload
                    distance = self._calculate_distance(truck['current_location'], delivery['pickup'])
                    if distance < min_distance:
                        min_distance = distance
                        new_truck_id = tid
            
            # If found a suitable truck, assign the delivery
            if new_truck_id:
                new_truck = self.trucks[new_truck_id]
                delivery = self.deliveries[delivery_id]
                delivery['status'] = 'in_progress'
                delivery['assigned_truck'] = new_truck_id
                new_truck['deliveries'].append(delivery_id)
                new_truck['total_weight'] += delivery['weight']
                new_truck['current_capacity'] -= delivery['weight']
                
                # Update route for new truck
                new_truck['current_route'] = self.optimize_route(new_truck_id, delivery_id)
            else:
                success = False
                print(f"Failed to reassign delivery {delivery_id}")
                
        return success

# Example usage
if __name__ == "__main__":
    # Initialize system
    routing_system = DynamicRoutingSystem()
    
    # Load truck data from Excel file
    routing_system.load_truck_data("GIS/Delivery truck trip data.xlsx")
    
    # Add some trucks
    routing_system.add_truck("T1", 5000, (20.5937, 78.9629))  # 5000 kg capacity
    routing_system.add_truck("T2", 3000, (19.0760, 72.8777))  # 3000 kg capacity
    
    # Add some deliveries
    routing_system.add_delivery("D1", (20.5937, 78.9629), (19.0760, 72.8777), 2000)  # 2000 kg
    routing_system.add_delivery("D2", (19.0760, 72.8777), (20.5937, 78.9629), 1500)  # 1500 kg
    
    # Assign deliveries
    routing_system.assign_delivery("D1")
    routing_system.assign_delivery("D2")
    
    # Visualize routes
    routing_system.visualize_routes() 