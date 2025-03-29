import random
import numpy as np
from typing import List, Tuple, Optional
from helper_functions import (
    euclidean_distance, 
    total_route_distance,
    calculate_visibility_matrix,
    calculate_route_quality,
    normalize_matrix
)

# -------------------------------
# CIACO (Clustering-Based Improved Ant Colony Optimization) Module
# -------------------------------

class CIACO:
    """
    Implementation of the CIACO (Clustering-Based Improved Ant Colony Optimization) algorithm.
    This version includes clustering-based initialization and improved ACO logic.
    
    Parameters:
        num_ants (int): Number of ants in the colony
        iterations (int): Number of iterations to run the algorithm
        alpha (float): Pheromone importance factor
        beta (float): Distance importance factor
        evaporation_rate (float): Rate at which pheromone evaporates
        initial_pheromone (float): Initial pheromone value
        return_to_depot (bool): Whether to return to the starting point
        num_clusters (int): Number of clusters for initialization
        elitist_factor (float): Factor for elitist pheromone update
    """
    def __init__(self, num_ants: int = 10, iterations: int = 50, alpha: float = 1.0, 
                 beta: float = 2.0, evaporation_rate: float = 0.1, 
                 initial_pheromone: float = 1.0, return_to_depot: bool = True,
                 num_clusters: int = 3, elitist_factor: float = 2.0):
        # Validate input parameters
        if num_ants <= 0:
            raise ValueError("Number of ants must be positive")
        if iterations <= 0:
            raise ValueError("Number of iterations must be positive")
        if alpha < 0:
            raise ValueError("Alpha must be non-negative")
        if beta < 0:
            raise ValueError("Beta must be non-negative")
        if not 0 <= evaporation_rate <= 1:
            raise ValueError("Evaporation rate must be between 0 and 1")
        if initial_pheromone <= 0:
            raise ValueError("Initial pheromone must be positive")
        if num_clusters <= 0:
            raise ValueError("Number of clusters must be positive")
        if elitist_factor < 1:
            raise ValueError("Elitist factor must be >= 1")

        self.num_ants = num_ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.initial_pheromone = initial_pheromone
        self.return_to_depot = return_to_depot
        self.num_clusters = num_clusters
        self.elitist_factor = elitist_factor
        
        # Initialize matrices
        self.pheromone_matrix: Optional[np.ndarray] = None
        self.distance_matrix: Optional[np.ndarray] = None
        self.visibility_matrix: Optional[np.ndarray] = None
        self.best_route: Optional[List[Tuple[float, float]]] = None
        self.best_distance = float('inf')
        self.stops: Optional[List[Tuple[float, float]]] = None
        self.clusters: Optional[List[List[int]]] = None

    def _cluster_stops(self) -> List[List[int]]:
        """
        Cluster the stops using K-means clustering.
        
        Returns:
            List of lists containing indices of stops in each cluster
        """
        if self.stops is None:
            raise RuntimeError("Stops not initialized")
            
        n = len(self.stops)
        if n <= self.num_clusters:
            return [[i] for i in range(n)]
            
        # Convert stops to numpy array for clustering
        points = np.array(self.stops)
        
        # Initialize centroids randomly
        centroids = points[random.sample(range(n), self.num_clusters)]
        
        # Perform K-means clustering
        for _ in range(100):  # Max iterations
            # Assign points to nearest centroid
            clusters = [[] for _ in range(self.num_clusters)]
            for i, point in enumerate(points):
                distances = [euclidean_distance(point, centroid) for centroid in centroids]
                cluster_idx = np.argmin(distances)
                clusters[cluster_idx].append(i)
                
            # Update centroids
            new_centroids = []
            for cluster in clusters:
                if cluster:
                    cluster_points = points[cluster]
                    new_centroid = np.mean(cluster_points, axis=0)
                    new_centroids.append(new_centroid)
                    
            # Check convergence
            if len(new_centroids) == len(centroids):
                if np.allclose(centroids, new_centroids, rtol=1e-5, atol=1e-5):
                    break
                    
            centroids = np.array(new_centroids)
            
        return clusters

    def _initialize_pheromones(self) -> None:
        """
        Initialize pheromone matrix using clustering information.
        """
        if self.stops is None or self.clusters is None:
            raise RuntimeError("Stops and clusters must be initialized")
            
        n = len(self.stops)
        self.pheromone_matrix = np.ones((n, n)) * self.initial_pheromone
        np.fill_diagonal(self.pheromone_matrix, 0)
        
        # Strengthen pheromone trails within clusters
        for cluster in self.clusters:
            for i in cluster:
                for j in cluster:
                    if i != j:
                        self.pheromone_matrix[i][j] *= 1.5
                        self.pheromone_matrix[j][i] *= 1.5

    def optimize_route(self, stops: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Optimize the route using the complete CIACO algorithm.
        
        Args:
            stops: List of coordinates (x, y) representing stops
            
        Returns:
            List of coordinates representing the optimized route
        """
        if not stops:
            raise ValueError("Stops list cannot be empty")
        
        if len(stops) <= 2:
            return stops

        self.stops = stops
        n = len(stops)

        # Initialize matrices
        self.distance_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                if i != j:
                    self.distance_matrix[i][j] = euclidean_distance(stops[i], stops[j])
                    self.distance_matrix[j][i] = self.distance_matrix[i][j]

        # Calculate visibility matrix
        self.visibility_matrix = calculate_visibility_matrix(stops)
        
        # Perform clustering
        self.clusters = self._cluster_stops()
        
        # Initialize pheromones with clustering information
        self._initialize_pheromones()

        # Main ACO loop
        for iteration in range(self.iterations):
            # Each ant constructs a solution
            ant_routes = []
            ant_distances = []
            
            for ant in range(self.num_ants):
                route = self._construct_solution()
                distance = total_route_distance(route, self.return_to_depot)
                ant_routes.append(route)
                ant_distances.append(distance)
                
                # Update best solution if found
                if distance < self.best_distance:
                    self.best_distance = distance
                    self.best_route = route

            # Update pheromones with elitist strategy
            self._update_pheromones(ant_routes, ant_distances)

        return self.best_route

    def _construct_solution(self) -> List[Tuple[float, float]]:
        """
        Construct a solution using the pheromone matrix and visibility information.
        """
        if self.stops is None or self.pheromone_matrix is None or self.visibility_matrix is None:
            raise RuntimeError("Algorithm not properly initialized")
            
        n = len(self.stops)
        unvisited = list(range(1, n))  # Start from index 0 (depot)
        current = 0
        route = [self.stops[0]]  # Start with depot

        while unvisited:
            # Calculate probabilities for each unvisited city
            probabilities = np.zeros(n)
            for next_city in unvisited:
                pheromone = self.pheromone_matrix[current][next_city] ** self.alpha
                visibility = self.visibility_matrix[current][next_city] ** self.beta
                probabilities[next_city] = pheromone * visibility

            # Normalize probabilities
            probabilities = normalize_matrix(probabilities)
            
            # Select next city using roulette wheel selection
            next_city = random.choices(range(n), weights=probabilities, k=1)[0]
            while next_city not in unvisited:
                next_city = random.choices(range(n), weights=probabilities, k=1)[0]

            route.append(self.stops[next_city])
            unvisited.remove(next_city)
            current = next_city

        # Return to depot if required
        if self.return_to_depot:
            route.append(self.stops[0])

        return route

    def _update_pheromones(self, ant_routes: List[List[Tuple[float, float]]], 
                          ant_distances: List[float]) -> None:
        """
        Update pheromone trails using elitist strategy.
        """
        if self.stops is None or self.pheromone_matrix is None:
            raise RuntimeError("Algorithm not properly initialized")

        # Evaporate pheromones
        self.pheromone_matrix *= (1 - self.evaporation_rate)

        # Find best ant in this iteration
        best_ant_idx = np.argmin(ant_distances)
        best_route = ant_routes[best_ant_idx]
        best_distance = ant_distances[best_ant_idx]

        # Update pheromones based on all ants
        for route, distance in zip(ant_routes, ant_distances):
            # Avoid division by zero
            contribution = 1.0 / (distance + 1e-10)  # Add small epsilon to avoid division by zero
            for i in range(len(route) - 1):
                current = self.stops.index(route[i])
                next_stop = self.stops.index(route[i + 1])
                self.pheromone_matrix[current][next_stop] += contribution
                self.pheromone_matrix[next_stop][current] += contribution

        # Apply elitist update to best route
        elitist_contribution = self.elitist_factor / (best_distance + 1e-10)  # Add small epsilon
        for i in range(len(best_route) - 1):
            current = self.stops.index(best_route[i])
            next_stop = self.stops.index(best_route[i + 1])
            self.pheromone_matrix[current][next_stop] += elitist_contribution
            self.pheromone_matrix[next_stop][current] += elitist_contribution