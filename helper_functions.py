import math
from typing import List, Tuple, Optional
import numpy as np

# -------------------------------
# Helper functions for CIACO Algorithm
# -------------------------------

def euclidean_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    """
    Calculate Euclidean distance between two locations.
    
    Args:
        loc1: First location coordinates (x, y)
        loc2: Second location coordinates (x, y)
        
    Returns:
        float: Euclidean distance between the two locations
    """
    return math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)

def total_route_distance(stops: List[Tuple[float, float]], return_to_depot: bool = True) -> float:
    """
    Calculate the total distance of a route given a list of stops.
    
    Args:
        stops: List of coordinates (x, y) representing stops
        return_to_depot: Whether to include return to starting point in distance
        
    Returns:
        float: Total distance of the route
    """
    if not stops:
        return 0.0
        
    distance = 0.0
    for i in range(len(stops) - 1):
        distance += euclidean_distance(stops[i], stops[i+1])
    
    # Add return to depot if required
    if return_to_depot and len(stops) > 1:
        distance += euclidean_distance(stops[-1], stops[0])
        
    return distance

def calculate_visibility_matrix(stops: List[Tuple[float, float]]) -> np.ndarray:
    """
    Calculate the visibility matrix (heuristic information) for the CIACO algorithm.
    Visibility is the inverse of distance.
    
    Args:
        stops: List of coordinates (x, y) representing stops
        
    Returns:
        np.ndarray: Visibility matrix
    """
    n = len(stops)
    visibility = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i != j:
                distance = euclidean_distance(stops[i], stops[j])
                visibility[i][j] = 1 / (distance + 1e-6)  # Add small constant to avoid division by zero
                
    return visibility

def calculate_route_quality(route: List[Tuple[float, float]], 
                          pheromone_matrix: np.ndarray,
                          visibility_matrix: np.ndarray,
                          alpha: float,
                          beta: float) -> float:
    """
    Calculate the quality of a route based on pheromone and visibility.
    
    Args:
        route: List of coordinates representing the route
        pheromone_matrix: Matrix of pheromone values
        visibility_matrix: Matrix of visibility values
        alpha: Pheromone importance factor
        beta: Visibility importance factor
        
    Returns:
        float: Route quality score
    """
    quality = 0.0
    for i in range(len(route) - 1):
        current_idx = route[i]
        next_idx = route[i + 1]
        pheromone = pheromone_matrix[current_idx][next_idx] ** alpha
        visibility = visibility_matrix[current_idx][next_idx] ** beta
        quality += pheromone * visibility
    return quality

def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
    """
    Normalize a matrix to sum to 1.
    
    Args:
        matrix: Input matrix to normalize
        
    Returns:
        np.ndarray: Normalized matrix
    """
    total = np.sum(matrix)
    if total == 0:
        return np.ones_like(matrix) / matrix.size
    return matrix / total