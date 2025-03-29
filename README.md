# Dynamic Delivery Management & Route Optimization System

## Overview
This system provides a dynamic truck routing and delivery management solution with real-time visualization. It uses the CIACO (Clustering-Based Improved Ant Colony Optimization) algorithm for route optimization and features a real-time GIS interface for monitoring truck movements and delivery assignments.

## Key Features
- **Real-time GIS Visualization**: Interactive map showing truck locations, routes, and delivery points
- **Dynamic Route Optimization**: Using CIACO algorithm to optimize routes
- **Ongoing Delivery Management**: Track truck locations, capacity, and route progress
- **Dynamic Delivery Assignment**: Add new orders during simulation and assign to available trucks
- **Simulation Controls**: Adjust simulation speed, number of trucks, and more

## System Components
- **CIACO Algorithm**: Core route optimization algorithm with clustering
- **Delivery Simulation**: Handles truck movement, order assignment, and status tracking
- **Interactive Dashboard**: GIS visualization with simulation controls
- **Truck & Order Management**: Tracks capacities, locations, and delivery status

## Usage Instructions

### Installation
1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Simulation
1. Start the application:
   ```
   python simulation_main.py
   ```
2. Access the dashboard at http://127.0.0.1:8050/

### Dashboard Controls
- **Initialize**: Set up trucks and orders according to slider values
- **Start/Stop/Reset**: Control simulation flow
- **Add Order**: Dynamically add new orders during simulation
- **Simulation Speed**: Adjust speed of truck movements
- **Number of Trucks/Orders**: Configure simulation parameters

## Implementation Details

### CIACO Algorithm
The CIACO algorithm is a clustering-based improvement on the Ant Colony Optimization technique, providing efficient route planning by:
- Clustering delivery points to segment the problem
- Optimizing routes within and between clusters
- Applying elitist pheromone strategies to improve convergence

### Dynamic Route Assignment
When a new delivery is added:
1. The system checks all ongoing trucks for remaining capacity
2. It evaluates route feasibility based on current positions and assigned deliveries
3. It updates routes for the selected truck using the CIACO algorithm
4. The GIS visualization displays the re-optimized route

### GIS Visualization
The system uses Plotly and Dash to provide:
- Real-time truck movement visualization
- Color-coded pickup and dropoff points
- Capacity and delivery status indicators
- Statistics on order completion rates

## File Structure
- `simulation_main.py`: Entry point for the application
- `gis_visualization.py`: GIS interface and simulation logic
- `CIACO_Algo.py`: Implementation of the optimization algorithm
- `Truck.py`: Class representing trucks with capacities and routes
- `Order.py`: Class representing delivery orders
- `helper_functions.py`: Utility functions for the CIACO algorithm

## Future Enhancements
- Integration with real-time traffic data
- Multi-depot optimization
- Time window constraints for deliveries
- Driver shift management
- Mobile application for drivers

## License
This project is licensed under the MIT License - see the LICENSE file for details. 