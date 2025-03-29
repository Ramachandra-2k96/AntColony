"""
Dynamic Routing System Test Cases

This module contains test cases for the dynamic routing system's core functionality.
Expected Test Results:

1. Sample Delivery Generation:
   - D1-D5 (Random weights 500-3000kg): Should PASS
   Reason: System should handle random delivery generation

2. Truck Movement Simulation:
   - T1 (Delhi): Should PASS (movement simulation)
   - T2 (Mumbai): Should PASS (movement simulation)
   - T3 (Bangalore): Should PASS (movement simulation)
   - T4 (Chennai): Should PASS (movement simulation)
   Reason: System should simulate truck movements correctly

3. Delivery Assignment:
   - All deliveries (D1-D5): Should PASS if:
     * Weight ≤ Truck Capacity
     * Truck available in appropriate location
     * No conflicting time windows
   - May FAIL if:
     * Weight exceeds truck capacity
     * No suitable truck available
     * Time window constraints not met
   Reason: System should properly assign deliveries based on constraints

4. Route Visualization:
   - All routes: Should PASS
   Reason: System should generate valid visualizations

Note: The actual results may vary based on:
- Random delivery generation
- Current system state
- Truck availability
- Time of execution
- System load
"""

from dynamic_routing import DynamicRoutingSystem
import time
import random

def generate_sample_deliveries(num_deliveries=5):
    """Generate sample delivery requests"""
    deliveries = []
    # Sample locations in India
    locations = [
        (20.5937, 78.9629),  # Delhi
        (19.0760, 72.8777),  # Mumbai
        (12.9716, 77.5946),  # Bangalore
        (13.0827, 80.2707),  # Chennai
        (22.5726, 88.3639),  # Kolkata
        (17.3850, 78.4867),  # Hyderabad
        (28.6139, 77.2090),  # New Delhi
        (19.2183, 72.9781),  # Thane
        (18.5204, 73.8567),  # Pune
        (23.2599, 77.4126)   # Bhopal
    ]
    
    for i in range(num_deliveries):
        pickup = random.choice(locations)
        dropoff = random.choice([loc for loc in locations if loc != pickup])
        weight = random.randint(500, 3000)  # Random weight between 500-3000 kg
        deliveries.append({
            'id': f'D{i+1}',
            'pickup': pickup,
            'dropoff': dropoff,
            'weight': weight
        })
    return deliveries

def simulate_truck_movement(routing_system, truck_id, duration_minutes=30):
    """Simulate truck movement along its route"""
    truck = routing_system.trucks[truck_id]
    if not truck['current_route']:
        return
    
    # Get route points
    route = truck['current_route']
    current_point = 0
    
    for _ in range(duration_minutes):
        if current_point >= len(route) - 1:
            break
            
        # Move truck to next point
        next_point = current_point + 1
        current_location = route[current_point]
        next_location = route[next_point]
        
        # Update truck location
        routing_system.update_truck_status(truck_id, next_location)
        
        # Update visualization
        routing_system.visualize_routes()
        
        current_point = next_point
        time.sleep(1)  # Simulate 1 minute of movement

def main():
    # Initialize the routing system
    routing_system = DynamicRoutingSystem()
    
    # Load truck data from Excel file
    routing_system.load_truck_data("GIS/Delivery truck trip data.xlsx")
    
    # Add trucks with different capacities
    trucks = [
        ("T1", 5000, (20.5937, 78.9629)),  # Delhi
        ("T2", 3000, (19.0760, 72.8777)),  # Mumbai
        ("T3", 4000, (12.9716, 77.5946)),  # Bangalore
        ("T4", 3500, (13.0827, 80.2707))   # Chennai
    ]
    
    for truck_id, capacity, location in trucks:
        routing_system.add_truck(truck_id, capacity, location)
    
    # Generate sample deliveries
    deliveries = generate_sample_deliveries(5)
    
    # Add deliveries to the system
    for delivery in deliveries:
        routing_system.add_delivery(
            delivery['id'],
            delivery['pickup'],
            delivery['dropoff'],
            delivery['weight']
        )
    
    print("Initial state:")
    routing_system.visualize_routes()
    
    # Assign deliveries to trucks
    print("\nAssigning deliveries...")
    for delivery in deliveries:
        success = routing_system.assign_delivery(delivery['id'])
        if success:
            print(f"Delivery {delivery['id']} assigned successfully")
        else:
            print(f"Failed to assign delivery {delivery['id']}")
    
    # Simulate truck movements
    print("\nSimulating truck movements...")
    for truck_id in routing_system.trucks:
        simulate_truck_movement(routing_system, truck_id, duration_minutes=5)
    
    print("\nSimulation completed. Check dynamic_routes.html for visualization.")

if __name__ == "__main__":
    main() 