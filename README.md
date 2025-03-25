# CIACO (Clustering-Based Improved Ant Colony Optimization)

This repository contains an implementation of the CIACO algorithm for solving the Traveling Salesman Problem (TSP) and similar routing problems. The algorithm combines clustering techniques with improved ant colony optimization to find efficient routes.

## Overview

CIACO is an enhanced version of the Ant Colony Optimization (ACO) algorithm that incorporates clustering to improve solution quality. It's particularly effective for:
- Delivery route optimization
- Vehicle routing problems
- Traveling salesman problems
- Any scenario requiring optimal path planning between multiple points

## Features

- **Clustering-based Initialization**: Groups nearby stops to improve initial solutions
- **Elitist Pheromone Update**: Reinforces the best solutions found
- **Multiple Configuration Options**: Test different parameter settings
- **Visualization Tools**: Plot routes and clusters
- **Performance Metrics**: Track solution quality and execution time

## Project Structure

```
.
├── CIACO_Algo.py      # Main algorithm implementation
├── helper_functions.py # Utility functions
├── main.py            # Testing and demonstration
└── README.md          # This file
```

## Dependencies

- Python 3.7+
- NumPy
- Matplotlib

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CIACO.git
cd CIACO
```

2. Install dependencies:
```bash
pip install numpy matplotlib
```

## Usage

### Basic Usage

```python
from CIACO_Algo import CIACO

# Create stops (example coordinates)
stops = [(0, 0), (1, 1), (2, 2), ...]

# Initialize the algorithm
aco = CIACO(
    num_ants=20,
    iterations=100,
    alpha=1.0,
    beta=2.0,
    evaporation_rate=0.1,
    initial_pheromone=1.0,
    return_to_depot=True,
    num_clusters=3,
    elitist_factor=2.0
)

# Find optimal route
route = aco.optimize_route(stops)
```

### Running Tests

```bash
python main.py
```

This will:
1. Test different problem sizes (10, 20, 30 stops)
2. Compare various configurations
3. Display performance metrics
4. Show route visualizations

## Algorithm Parameters

- `num_ants`: Number of ants in the colony
- `iterations`: Number of iterations to run
- `alpha`: Pheromone importance factor
- `beta`: Distance importance factor
- `evaporation_rate`: Rate at which pheromone evaporates
- `initial_pheromone`: Initial pheromone value
- `return_to_depot`: Whether to return to starting point
- `num_clusters`: Number of clusters for initialization
- `elitist_factor`: Factor for elitist pheromone update

## Test Configurations

The code includes four test configurations:

1. **Basic**
   - Simple ACO implementation
   - Fast execution
   - Suitable for small problems

2. **Enhanced**
   - More ants and iterations
   - Better solution quality
   - Longer execution time

3. **Clustered**
   - Uses clustering-based initialization
   - Balanced performance
   - Good for medium-sized problems

4. **Elitist**
   - Uses elitist pheromone update
   - Strong reinforcement of best solutions
   - Effective for larger problems

## Visualization

The code includes visualization tools that show:
- All stops as dots
- The depot (starting point) in green
- The optimized route as a blue line
- Clusters in different colors (when clustering is used)

## Performance Metrics

The algorithm tracks:
- Total route distance
- Execution time
- Solution quality
- Convergence behavior

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the Ant Colony Optimization algorithm
- Enhanced with clustering techniques
- Inspired by real-world routing problems 