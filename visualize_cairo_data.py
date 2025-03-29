#!/usr/bin/env python3
"""
Script to visualize CIACO routes using actual Cairo data from a CSV file.
This uses actual road network paths instead of direct connections.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from aco_visualization import ACOVisualization
import folium

def main():
    """Main function to visualize Cairo data"""
    print("Visualizing CIACO routes with actual Cairo data")
    
    # Initialize the visualization class
    vis = ACOVisualization()
    
    try:
        # Load Cairo data from CSV file
        print("Loading Cairo data from CSV...")
        vis.load_data_from_csv('Cairo_data.csv')
        
        # Set starting point as the depot
        start_point = None
        if 'color' in vis.location_data.columns:
            # If the data has a color column, use the 'green' point as the depot
            depot_row = vis.location_data[vis.location_data['color'] == 'green']
            if not depot_row.empty:
                start_point = (depot_row.iloc[0]['y'], depot_row.iloc[0]['x'])
                print(f"Using depot from data: {start_point}")
        
        if start_point is None and len(vis.location_data) > 0:
            # If no depot found, use the first point as the depot
            start_point = (vis.location_data.iloc[0]['y'], vis.location_data.iloc[0]['x'])
            print(f"Using first point as depot: {start_point}")
        
        # Create street network around the starting point
        print("Creating street network for Cairo...")
        vis.create_street_network(center_point=start_point, distance=25000)
        
        # Create trucks at the depot location
        print("Creating delivery trucks...")
        num_trucks = 3  # Adjust the number of trucks as needed
        vis.create_trucks(num_trucks=num_trucks, max_capacity=1500, start_location=start_point)
        
        # Create pickup/delivery orders between random locations (excluding the depot)
        print("Creating delivery orders...")
        non_depot_locations = vis.location_data.copy()
        
        # Skip the depot when creating orders
        if 'color' in non_depot_locations.columns:
            non_depot_locations = non_depot_locations[non_depot_locations['color'] != 'green']
        elif len(non_depot_locations) > 1:
            non_depot_locations = non_depot_locations.iloc[1:]
        
        # Create fake orders using the points as either pickup or delivery
        orders_data = []
        for i in range(min(15, len(non_depot_locations))):
            # Create a pickup and delivery pair
            if i < len(non_depot_locations) - 1:
                pickup_idx = i
                delivery_idx = i + 1
            else:
                pickup_idx = i
                delivery_idx = 0
                
            pickup = (non_depot_locations.iloc[pickup_idx]['y'], non_depot_locations.iloc[pickup_idx]['x'])
            delivery = (non_depot_locations.iloc[delivery_idx]['y'], non_depot_locations.iloc[delivery_idx]['x'])
            
            orders_data.append({
                'order_id': f'O{i+1}',
                'weight': np.random.randint(100, 500),
                'pickup': pickup,
                'delivery': delivery
            })
        
        # Manually create orders
        for order_data in orders_data:
            vis.orders[order_data['order_id']] = Order(
                order_data['order_id'],
                order_data['weight'],
                order_data['pickup'],
                order_data['delivery']
            )
            
        print(f"Created {len(vis.orders)} orders")
        
        # Assign orders to trucks using balanced strategy
        print("Assigning orders to trucks...")
        vis.assign_orders_to_trucks(strategy="balanced")
        
        # Optimize routes with CIACO
        print("Optimizing routes with CIACO algorithm...")
        vis.optimize_routes()
        
        # Create the map visualization with actual road paths
        print("Creating map visualization with actual road paths...")
        map_obj = vis.visualize_on_map(center=start_point, use_road_network=True)
        
        # Add the starting point (depot) with a special marker
        folium.Marker(
            location=start_point,
            popup="Depot",
            icon=folium.Icon(color='green', icon='home', prefix='fa')
        ).add_to(map_obj)
        
        # Save the map
        map_file = "cairo_routes_real_data.html"
        map_obj.save(map_file)
        print(f"Map saved to {map_file}")
        
        # Create capacity timeline
        print("Creating capacity timeline...")
        fig, _ = vis.visualize_capacity_timeline(figsize=(14, 10))
        
        # Save the capacity timeline
        timeline_file = "cairo_capacity_timeline_real_data.png"
        plt.savefig(timeline_file, dpi=300, bbox_inches="tight")
        print(f"Capacity timeline saved to {timeline_file}")
        
        print("\nVisualization complete!")
        print(f"Open {map_file} in a web browser to see the interactive map")
        print(f"Open {timeline_file} to see the capacity constraints visualization")
        
    except FileNotFoundError:
        print("Error: Cairo_data.csv file not found")
        print("Please make sure the CSV file is in the current directory")
        print("The file should have columns for id, Latitude/y, and Longitude/x")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Import Order class inside the __main__ block to avoid circular imports
    from Order import Order
    main() 