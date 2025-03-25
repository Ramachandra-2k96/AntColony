import pandas as pd
import folium
from folium import plugins
import numpy as np
from datetime import datetime
import random
from typing import List, Tuple, Dict
import json

class GISVisualizer:
    def __init__(self, csv_path: str):
        """Initialize the GIS Visualizer with the path to the orders CSV file."""
        self.csv_path = csv_path
        self.orders_df = None
        self.map = None
        # Bangalore center coordinates
        self.center_lat = 12.9716
        self.center_lon = 77.5946
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the orders data."""
        columns = ['Order_ID', 'Grid_ID', 'Order_Type', 'Preparation_Time', 
                  'Date', 'Day_of_Week', 'Hour_of_Day']
        self.orders_df = pd.read_csv(self.csv_path, usecols=columns)
        
        # Define Bangalore area bounds
        self.bounds = {
            'north': 13.0827,
            'south': 12.8254,
            'east': 77.7479,
            'west': 77.4855
        }
        
        # Convert Grid_ID to actual Bangalore coordinates based on zones
        # This is a simplified mapping - you should replace with actual grid mapping
        bangalore_zones = {
            'central': (12.9716, 77.5946),
            'electronic_city': (12.8458, 77.5929),
            'whitefield': (12.9698, 77.7500),
            'koramangala': (12.9279, 77.6271),
            'indiranagar': (12.9719, 77.6412)
        }
        
        # Assign coordinates based on Grid_ID zones
        def assign_coordinates(grid_id):
            zone = random.choice(list(bangalore_zones.keys()))
            base_lat, base_lon = bangalore_zones[zone]
            # Add small random offset within the zone
            lat = base_lat + random.uniform(-0.01, 0.01)
            lon = base_lon + random.uniform(-0.01, 0.01)
            return pd.Series({'latitude': lat, 'longitude': lon})
            
        coords_df = self.orders_df['Grid_ID'].apply(assign_coordinates)
        self.orders_df['latitude'] = coords_df['latitude']
        self.orders_df['longitude'] = coords_df['longitude']
        
    def create_base_map(self):
        """Create a base map centered on Bangalore."""
        self.map = folium.Map(
            location=[self.center_lat, self.center_lon],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
    def add_delivery_zone_boundary(self):
        """Add the delivery zone boundary polygon."""
        boundary_coords = [
            [12.9716, 77.4855],  # West
            [12.9716, 77.7479],  # East
            [12.8254, 77.7479],  # Southeast
            [12.8254, 77.4855],  # Southwest
        ]
        
        folium.PolyLine(
            locations=boundary_coords,
            color='blue',
            weight=2,
            opacity=0.8
        ).add_to(self.map)
        
    def visualize_delivery_clusters(self, num_points: int = 50):
        """Visualize delivery points with enhanced heatmap clusters."""
        if self.map is None:
            self.create_base_map()
            
        # Sample points for visualization
        sample_df = self.orders_df.sample(n=min(num_points, len(self.orders_df)))
        
        # Add enhanced heatmap with string keys for gradient
        heat_data = [[row['latitude'], row['longitude'], 0.5] for _, row in sample_df.iterrows()]
        plugins.HeatMap(
            heat_data,
            radius=15,
            blur=10,
            max_zoom=13,
            gradient={
                '0.4': 'blue',
                '0.65': 'lime',
                '0.8': 'orange',
                '1.0': 'red'
            }
        ).add_to(self.map)
        
        # Add markers with custom icons
        for _, row in sample_df.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=f"Order ID: {row['Order_ID']}<br>Type: {row['Order_Type']}",
                color='red',
                fill=True,
                fill_color='red'
            ).add_to(self.map)
            
        # Add the delivery zone boundary
        self.add_delivery_zone_boundary()
        
        return self.map
    
    def visualize_route(self, route_points: List[Tuple[float, float]], 
                       color: str = 'blue', weight: int = 3):
        """Visualize a delivery route."""
        if self.map is None:
            self.create_base_map()
            
        folium.PolyLine(
            locations=route_points,
            color=color,
            weight=weight,
            opacity=0.8
        ).add_to(self.map)
        
        return self.map
    
    def save_map(self, output_path: str = 'bangalore_delivery_map.html'):
        """Save the map to an HTML file."""
        if self.map is not None:
            self.map.save(output_path)

def main():
    visualizer = GISVisualizer('processed_orders.csv')
    
    # Create visualization with delivery clusters
    visualizer.visualize_delivery_clusters(50)
    
    # Save the map
    visualizer.save_map('bangalore_delivery_map.html')

if __name__ == "__main__":
    main() 