# Ant Colony Optimization Route Visualization

This visualization tool allows you to visualize the results of the CIACO (Clustering-Based Improved Ant Colony Optimization) algorithm for delivery route optimization with capacity constraints.

## Features

- Interactive map showing optimized delivery routes
- **Actual road network paths** instead of straight-line connections
- Multiple truck support with capacity constraints
- Pickup and dropoff visualization
- Capacity timeline graphs showing how truck loads change during the route
- Support for different order assignment strategies

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure you have the following files in your project:
   - `CIACO_Algo.py` - The ant colony optimization algorithm
   - `Truck.py` - The truck class definition
   - `Order.py` - The order class definition
   - `aco_visualization.py` - The visualization module

## Quick Start

Run the example script to see the visualization in action:

```bash
python visualize_aco_routes.py
```

This will:
1. Create sample data for Cairo
2. Generate a street network using OpenStreetMap data
3. Generate trucks and delivery orders
4. Assign orders to trucks using a balanced strategy
5. Optimize routes using the CIACO algorithm
6. Create and save an interactive map with actual road paths (`cairo_routes.html`)
7. Generate a capacity timeline visualization (`cairo_capacity_timeline.png`)

## Usage

### Basic Usage

```python
from aco_visualization import ACOVisualization
import pandas as pd

# Create or load location data
locations = pd.DataFrame({
    'id': [0, 1, 2, 3, 4],
    'y': [30.044, 30.054, 30.064, 30.074, 30.084],  # Latitudes
    'x': [31.236, 31.246, 31.256, 31.266, 31.276],  # Longitudes
})

# Initialize the visualization
vis = ACOVisualization(locations)

# Create street network (required for road path visualization)
vis.create_street_network(center_point=(30.044, 31.236), distance=10000)

# Create trucks
vis.create_trucks(num_trucks=2, max_capacity=1000)

# Create orders
vis.create_orders(num_orders=5, max_weight=400)

# Assign orders to trucks
vis.assign_orders_to_trucks(strategy="balanced")

# Optimize routes
vis.optimize_routes()

# Create and save map visualization with actual road paths
map_obj = vis.visualize_on_map(use_road_network=True)
map_obj.save("routes.html")

# Create and save capacity timeline
import matplotlib.pyplot as plt
fig, _ = vis.visualize_capacity_timeline()
plt.savefig("capacity_timeline.png")
```

### Loading Data from a CSV File

If you have location data in a CSV file, you can load it directly:

```python
vis = ACOVisualization()
vis.load_data_from_csv("locations.csv")
```

The CSV file should have columns for location ID, latitude (y), and longitude (x).

### Creating a Street Network

For realistic routing using actual roads, you should create a street network:

```python
vis.create_street_network(center_point=(30.044, 31.236), distance=10000)
```

This will download OpenStreetMap data for the specified area and create a road network graph.

### Road Network vs. Direct Connections

You can choose whether to show actual road paths or direct connections:

```python
# With actual road paths (default)
map_obj = vis.visualize_on_map(use_road_network=True)

# With direct connections (faster but less realistic)
map_obj = vis.visualize_on_map(use_road_network=False)
```

Actual road paths show the precise routes vehicles would take on real roads.

### Assignment Strategies

Three assignment strategies are available:

- `"greedy"`: Assign orders to trucks with the most remaining capacity
- `"balanced"`: Distribute orders evenly among trucks based on weight
- `"nearest"`: Assign orders to the nearest truck with sufficient capacity

```python
vis.assign_orders_to_trucks(strategy="nearest")
```

## Understanding the Visualizations

### Map Visualization

The interactive map shows:
- Trucks (green markers)
- Pickup locations (blue up-arrow markers)
- Dropoff locations (red down-arrow markers)
- Optimized routes (colored lines following actual roads)
- Unassigned orders (orange markers)

Hover or click on any marker to see detailed information.

### Capacity Timeline

The capacity timeline shows how each truck's load changes during its route:
- The horizontal axis represents stops along the route
- The vertical axis shows the remaining capacity
- Pickups decrease the remaining capacity (steps down)
- Dropoffs increase the remaining capacity (steps up)
- The red dashed line shows the maximum capacity

## Advanced Configuration

You can customize the ACO algorithm parameters by modifying the CIACO initialization:

```python
vis.ciaco = CIACO(
    num_ants=20,         # Number of ants in the colony
    iterations=100,      # Number of iterations
    alpha=1.0,           # Pheromone importance factor
    beta=2.0,            # Distance importance factor
    evaporation_rate=0.1 # Pheromone evaporation rate
)
``` 