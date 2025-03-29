#!/usr/bin/env python3
"""
Example script demonstrating the ACO Visualization with custom data.
This script shows how to visualize routes optimized with the CIACO algorithm,
including truck capacity constraints during pickup and delivery operations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from aco_visualization import ACOVisualization

def load_sample_data():
    """Create a sample dataset of locations in Cairo"""
    # Example Cairo coordinates
    cairo_center = (30.0444, 31.2357)
    
    # Create random points around Cairo center
    num_points = 20
    np.random.seed(42)  # For reproducibility
    
    # Generate random points around Cairo center (±0.1 degrees)
    lats = np.random.uniform(cairo_center[0] - 0.1, cairo_center[0] + 0.1, num_points)
    lons = np.random.uniform(cairo_center[1] - 0.1, cairo_center[1] + 0.1, num_points)
    
    # Create DataFrame
    locations = pd.DataFrame({
        'id': range(num_points),
        'y': lats,  # Latitude
        'x': lons,  # Longitude
    })
    
    return locations

def main():
    """Main function to run the visualization"""
    print("Creating ACO visualization for Cairo delivery routes")
    
    # Load sample data
    locations = load_sample_data()
    print(f"Created {len(locations)} sample locations in Cairo")
    
    # Initialize the visualization
    vis = ACOVisualization(locations)
    
    # Create street network for Cairo (explicitly create the network first)
    cairo_center = (30.0444, 31.2357)
    print("Creating street network for Cairo...")
    vis.create_street_network(center_point=cairo_center, distance=15000)
    print("Street network created")
    
    # Create trucks with different capacities
    vis.create_trucks(num_trucks=3, max_capacity=1000)
    print("Created 3 delivery trucks with varying capacities")
    
    # Create orders with different weights
    vis.create_orders(num_orders=10, max_weight=400)
    print("Created 10 delivery orders with varying weights")
    
    # Assign orders to trucks (balanced strategy)
    print("Assigning orders to trucks using balanced strategy...")
    vis.assign_orders_to_trucks(strategy="balanced")
    
    # Optimize routes using CIACO algorithm
    print("Optimizing routes using CIACO algorithm...")
    vis.optimize_routes()
    
    # Visualize the routes on a map with actual road paths
    print("Generating map visualization with actual road paths...")
    map_obj = vis.visualize_on_map(use_road_network=True)
    map_obj.save("cairo_routes.html")
    print("Map saved to cairo_routes.html")
    
    # Visualize the capacity timeline
    print("Generating capacity timeline visualization...")
    fig, _ = vis.visualize_capacity_timeline(figsize=(12, 8))
    plt.savefig("cairo_capacity_timeline.png", dpi=300, bbox_inches="tight")
    print("Capacity timeline saved to cairo_capacity_timeline.png")
    
    print("\nVisualization complete!")
    print("Open cairo_routes.html in a web browser to see the interactive map")
    print("Open cairo_capacity_timeline.png to see the capacity constraints visualization")

if __name__ == "__main__":
    main() 