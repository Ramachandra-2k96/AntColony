import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from CIACO_Algo import CIACO
from helper_functions import total_route_distance
import time
import random


def generate_random_stops(num_stops: int, x_range: Tuple[float, float] = (0, 100), 
                         y_range: Tuple[float, float] = (0, 100)) -> List[Tuple[float, float]]:
    """
    Generate random stops for testing the CIACO algorithm.
    
    Args:
        num_stops: Number of stops to generate
        x_range: Range for x coordinates
        y_range: Range for y coordinates
        
    Returns:
        List of (x, y) coordinates
    """
    return [(random.uniform(x_range[0], x_range[1]), 
             random.uniform(y_range[0], y_range[1])) 
            for _ in range(num_stops)]

def plot_route(stops: List[Tuple[float, float]], route: List[Tuple[float, float]], 
               title: str = "Route Visualization", show_clusters: bool = False,
               clusters: List[List[int]] = None):
    """
    Plot the route and stops using matplotlib.
    
    Args:
        stops: List of all stops
        route: List of stops in the route order
        title: Title for the plot
        show_clusters: Whether to show cluster assignments
        clusters: List of cluster assignments
    """
    plt.figure(figsize=(10, 10))
    
    # Plot all stops
    x_coords = [stop[0] for stop in stops]
    y_coords = [stop[1] for stop in stops]
    
    if show_clusters and clusters:
        # Plot stops with different colors for each cluster
        colors = plt.cm.rainbow(np.linspace(0, 1, len(clusters)))
        for cluster_idx, cluster in enumerate(clusters):
            cluster_x = [stops[i][0] for i in cluster]
            cluster_y = [stops[i][1] for i in cluster]
            plt.scatter(cluster_x, cluster_y, c=[colors[cluster_idx]], 
                       label=f'Cluster {cluster_idx + 1}')
    else:
        plt.scatter(x_coords, y_coords, c='red', label='Stops')
    
    # Plot the route
    route_x = [stop[0] for stop in route]
    route_y = [stop[1] for stop in route]
    plt.plot(route_x, route_y, 'b-', label='Route')
    
    # Highlight the depot (first stop)
    plt.scatter(route_x[0], route_y[0], c='green', s=100, label='Depot')
    
    plt.title(title)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.legend()
    plt.grid(True)
    plt.show()

def test_algorithm(num_stops: int = 20, num_tests: int = 5):
    """
    Test the CIACO algorithm with different parameters and configurations.
    
    Args:
        num_stops: Number of stops to generate
        num_tests: Number of test runs
    """
    print(f"\nTesting CIACO Algorithm with {num_stops} stops")
    print("=" * 50)
    
    # Test configurations
    configs = [
        {"config": {"num_ants": 10, "iterations": 50}, "name": "Basic"},
        {"config": {"num_ants": 20, "iterations": 100}, "name": "Enhanced"},
        {"config": {"num_ants": 15, "iterations": 75, "num_clusters": 3}, "name": "Clustered"},
        {"config": {"num_ants": 20, "iterations": 100, "elitist_factor": 3.0}, "name": "Elitist"}
    ]
    
    for config in configs:
        print(f"\nTesting {config['name']} Configuration:")
        print("-" * 30)
        
        total_time = 0
        total_distance = 0
        best_distance = float('inf')
        
        for test in range(num_tests):
            # Generate random stops
            stops = generate_random_stops(num_stops)
            
            # Create CIACO instance with current configuration
            aco = CIACO(**config['config'])
            
            # Run optimization
            start_time = time.time()
            route = aco.optimize_route(stops)
            end_time = time.time()
            
            # Calculate metrics
            distance = total_route_distance(route)
            execution_time = end_time - start_time
            
            total_time += execution_time
            total_distance += distance
            best_distance = min(best_distance, distance)
            
            print(f"Test {test + 1}:")
            print(f"  Distance: {distance:.2f}")
            print(f"  Time: {execution_time:.2f}s")
            
            # Plot the first test run for each configuration
            if test == 0:
                plot_route(stops, route, 
                          title=f"{config['name']} Configuration - Test 1",
                          show_clusters=True,
                          clusters=aco.clusters)
        
        # Print average metrics
        print("\nAverage Metrics:")
        print(f"  Average Distance: {total_distance/num_tests:.2f}")
        print(f"  Average Time: {total_time/num_tests:.2f}s")
        print(f"  Best Distance: {best_distance:.2f}")

def main():
    """
    Main function to demonstrate the CIACO algorithm.
    """
    # Test with different problem sizes
    problem_sizes = [10, 20, 30]
    
    for size in problem_sizes:
        print(f"\nTesting with {size} stops")
        test_algorithm(num_stops=size, num_tests=3)
        
        # Generate a sample problem and solve it
        stops = generate_random_stops(size)
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
        
        route = aco.optimize_route(stops)
        distance = total_route_distance(route)
        
        print(f"\nSample Problem Results:")
        print(f"Total Distance: {distance:.2f}")
        plot_route(stops, route, 
                  title=f"Sample Problem with {size} stops",
                  show_clusters=True,
                  clusters=aco.clusters)

if __name__ == "__main__":
    main()
