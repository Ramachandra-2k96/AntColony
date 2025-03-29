#!/usr/bin/env python3
"""
Script to visualize CIACO routes for Bangalore delivery operations.
This script demonstrates the improved visualization with:
1. Clear truck differentiation
2. Actual road network paths
3. Marker clustering for overlapping points
4. Proper capacity constraints
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from improved_aco_visualization import ImprovedACOVisualization, generate_bangalore_data
import folium
from Order import Order

def main():
    """Main function to run the Bangalore visualization"""
    print("Visualizing CIACO routes for Bangalore delivery operations")
    
    # Generate Bangalore sample data (or load from CSV if available)
    try:
        print("Attempting to load Bangalore data from CSV...")
        vis = ImprovedACOVisualization()
        vis.load_data_from_csv('bangalore_data.csv')
        bangalore_center = (12.9716, 77.5946)  # Default Bangalore center
    except:
        print("CSV not found, generating sample Bangalore data...")
        locations, bangalore_center = generate_bangalore_data(num_points=20)
        vis = ImprovedACOVisualization(locations)
    
    print(f"Working with {len(vis.location_data)} locations in Bangalore")
    
    # Create street network for Bangalore
    print("Creating street network for Bangalore...")
    vis.create_street_network(center_point=bangalore_center, distance=15000, city="Bangalore, India")
    
    # Find the depot location (green point or first point)
    depot_location = None
    if 'color' in vis.location_data.columns:
        depot_rows = vis.location_data[vis.location_data['color'] == 'green']
        if not depot_rows.empty:
            depot_location = (depot_rows.iloc[0]['y'], depot_rows.iloc[0]['x'])
    
    if depot_location is None and len(vis.location_data) > 0:
        depot_location = (vis.location_data.iloc[0]['y'], vis.location_data.iloc[0]['x'])
    
    # Create trucks with slightly different starting positions
    print("Creating trucks...")
    if depot_location:
        # Create 3 trucks with small position offsets for better visibility
        start_locations = [
            depot_location,  # Exact depot location
            (depot_location[0] + 0.0008, depot_location[1] - 0.0005),  # Small offset 1
            (depot_location[0] - 0.0006, depot_location[1] + 0.0008)   # Small offset 2
        ]
        vis.create_trucks(num_trucks=3, max_capacity=1500, start_locations=start_locations)
    else:
        # Default creation if no depot found
        vis.create_trucks(num_trucks=3, max_capacity=1500)
    
    # Create orders between random locations
    print("Creating delivery orders...")
    vis.create_orders(num_orders=15, max_weight=400)
    
    # Assign orders to trucks with balanced strategy
    print("Assigning orders to trucks...")
    vis.assign_orders_to_trucks(strategy="balanced")
    
    # Optimize routes using the CIACO algorithm
    print("Optimizing routes with CIACO algorithm...")
    vis.optimize_routes()
    
    # Create map visualization with actual road network and marker clustering
    print("Creating map visualization...")
    map_obj = vis.visualize_on_map(center=bangalore_center, use_road_network=True, use_marker_clusters=True)
    
    # Add title to map
    title_html = '''
    <h3 align="center" style="font-size:16px"><b>Bangalore Delivery Routes - ACO Optimization</b></h3>
    <div align="center">
        Green: Trucks | Blue: Pickups | Red: Dropoffs<br>
        Click markers or routes for details
    </div>
    '''
    map_obj.get_root().html.add_child(folium.Element(title_html))
    
    # Save map to HTML file
    map_file = "bangalore_routes.html"
    map_obj.save(map_file)
    print(f"Interactive map saved to {map_file}")
    
    # Create capacity timeline visualization
    print("Creating capacity timeline visualization...")
    fig, _ = vis.visualize_capacity_timeline(figsize=(14, 8))
    
    # Save timeline
    timeline_file = "bangalore_capacity_timeline.png"
    plt.savefig(timeline_file, dpi=300, bbox_inches="tight")
    print(f"Capacity timeline saved to {timeline_file}")
    
    print("\nVisualization complete!")
    print(f"Open {map_file} in a web browser to see the interactive map")
    print(f"Open {timeline_file} to see the capacity constraints visualization")

if __name__ == "__main__":
    main() 