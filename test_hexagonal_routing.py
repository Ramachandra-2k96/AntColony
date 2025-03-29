"""
Test Cases for Hexagonal Routing System

This module contains test cases for the hexagonal routing system implementation.
Expected Test Results:

1. Same Hexagon Deliveries (All Should PASS):
   - SH1 (Delhi to Delhi, 1000kg): Should PASS
   - SH2 (Mumbai to Mumbai, 1500kg): Should PASS
   - SH3 (Bangalore to Bangalore, 2000kg): Should PASS
   Reason: Deliveries within same hexagon should be easier to handle

2. Cross Hexagon Deliveries (All Should PASS):
   - CH1 (Delhi to Mumbai, 1000kg): Should PASS
   - CH2 (Bangalore to Chennai, 1500kg): Should PASS
   - CH3 (Mumbai to Bangalore, 2000kg): Should PASS
   Reason: System should handle cross-hexagon deliveries

3. Capacity Constraints (Mixed Results):
   - CT1 (4500kg): Should FAIL (exceeds truck capacity)
   - CT2 (1000kg): Should PASS (within capacity)
   - CT3 (3000kg): Should FAIL (exceeds available capacity)
   Reason: System should enforce capacity constraints

4. Multiple Deliveries per Truck (Mixed Results):
   - M1 (1000kg): Should PASS (assigned to T1)
   - M2 (1500kg): Should PASS (assigned to T2)
   - M3 (1000kg): Should PASS (assigned to T4)
   - M4 (2000kg): Should FAIL (no suitable truck available)
   Reason: System should manage multiple deliveries while respecting capacity

5. Time Window Deliveries (Mixed Results):
   - TW1 (4-hour window): Should PASS (assigned to T4)
   - TW2 (4-hour window): Should FAIL (time window too late)
   - TW3 (4-hour window): Should FAIL (time window too late)
   Reason: System should respect time window constraints

6. Emergency Rerouting (Should PASS):
   - Truck T1 breakdown: Should PASS
   Reason: System should handle truck breakdowns by reassigning deliveries

Note: The actual results may vary based on the current state of the system,
truck availability, and other dynamic factors.
"""

from dynamic_routing import DynamicRoutingSystem
import time
import random
from datetime import datetime, timedelta

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
    
    # Generate deliveries within the same hexagon
    print("\n=== Testing Deliveries Within Same Hexagon ===")
    same_hex_deliveries = [
        ("SH1", (20.5937, 78.9629), (20.5937, 78.9629), 1000),  # Delhi to Delhi
        ("SH2", (19.0760, 72.8777), (19.0760, 72.8777), 1500),  # Mumbai to Mumbai
        ("SH3", (12.9716, 77.5946), (12.9716, 77.5946), 2000)   # Bangalore to Bangalore
    ]
    
    for delivery_id, pickup, dropoff, weight in same_hex_deliveries:
        routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
        success = routing_system.assign_delivery(delivery_id)
        print(f"Same hexagon delivery {delivery_id} assigned: {'Success' if success else 'Failed'}")
    
    routing_system.visualize_routes()
    
    # Generate deliveries between different hexagons
    print("\n=== Testing Deliveries Between Hexagons ===")
    cross_hex_deliveries = [
        ("CH1", (20.5937, 78.9629), (19.0760, 72.8777), 1000),  # Delhi to Mumbai
        ("CH2", (12.9716, 77.5946), (13.0827, 80.2707), 1500),  # Bangalore to Chennai
        ("CH3", (19.0760, 72.8777), (12.9716, 77.5946), 2000)   # Mumbai to Bangalore
    ]
    
    for delivery_id, pickup, dropoff, weight in cross_hex_deliveries:
        routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
        success = routing_system.assign_delivery(delivery_id)
        print(f"Cross hexagon delivery {delivery_id} assigned: {'Success' if success else 'Failed'}")
    
    routing_system.visualize_routes()
    
    # Test capacity constraints
    print("\n=== Testing Capacity Constraints ===")
    capacity_test_deliveries = [
        ("CT1", (20.5937, 78.9629), (19.0760, 72.8777), 4500),  # Almost full truck
        ("CT2", (12.9716, 77.5946), (13.0827, 80.2707), 1000),  # Small delivery
        ("CT3", (19.0760, 72.8777), (12.9716, 77.5946), 3000)   # Large delivery
    ]
    
    for delivery_id, pickup, dropoff, weight in capacity_test_deliveries:
        routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
        success = routing_system.assign_delivery(delivery_id)
        print(f"Capacity test delivery {delivery_id} ({weight}kg) assigned: {'Success' if success else 'Failed'}")
    
    routing_system.visualize_routes()
    
    # Test multiple deliveries per truck
    print("\n=== Testing Multiple Deliveries per Truck ===")
    multiple_deliveries = [
        ("M1", (20.5937, 78.9629), (19.0760, 72.8777), 1000),  # Delhi to Mumbai
        ("M2", (19.0760, 72.8777), (12.9716, 77.5946), 1500),  # Mumbai to Bangalore
        ("M3", (12.9716, 77.5946), (13.0827, 80.2707), 1000),  # Bangalore to Chennai
        ("M4", (13.0827, 80.2707), (20.5937, 78.9629), 2000)   # Chennai to Delhi
    ]
    
    for delivery_id, pickup, dropoff, weight in multiple_deliveries:
        routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
        success = routing_system.assign_delivery(delivery_id)
        print(f"Multiple delivery {delivery_id} ({weight}kg) assigned: {'Success' if success else 'Failed'}")
        if success:
            truck_id = routing_system.deliveries[delivery_id]['assigned_truck']
            truck = routing_system.trucks[truck_id]
            print(f"  Assigned to truck {truck_id} (Total weight: {truck['total_weight']}/{truck['max_capacity']}kg)")
    
    routing_system.visualize_routes()
    
    # Test time window deliveries with more realistic windows
    print("\n=== Testing Time Window Deliveries ===")
    now = datetime.now()
    time_window_deliveries = [
        ("TW1", (20.5937, 78.9629), (19.0760, 72.8777), 1000, 
         (now + timedelta(hours=1), now + timedelta(hours=5))),  # 4-hour window
        ("TW2", (12.9716, 77.5946), (13.0827, 80.2707), 1500,
         (now + timedelta(hours=2), now + timedelta(hours=6))),  # 4-hour window
        ("TW3", (19.0760, 72.8777), (12.9716, 77.5946), 2000,
         (now + timedelta(hours=3), now + timedelta(hours=7)))   # 4-hour window
    ]
    
    for delivery_id, pickup, dropoff, weight, time_window in time_window_deliveries:
        routing_system.add_delivery(delivery_id, pickup, dropoff, weight, time_window)
        success = routing_system.assign_delivery(delivery_id)
        print(f"Time window delivery {delivery_id} assigned: {'Success' if success else 'Failed'}")
        print(f"Time window: {time_window[0].strftime('%H:%M')} - {time_window[1].strftime('%H:%M')}")
        if success:
            truck_id = routing_system.deliveries[delivery_id]['assigned_truck']
            truck = routing_system.trucks[truck_id]
            print(f"  Assigned to truck {truck_id} (Total weight: {truck['total_weight']}/{truck['max_capacity']}kg)")
    
    routing_system.visualize_routes()
    
    # Test emergency rerouting with detailed reporting
    print("\n=== Testing Emergency Rerouting ===")
    print("Simulating truck breakdown...")
    truck_id = "T1"
    if truck_id in routing_system.trucks:
        truck = routing_system.trucks[truck_id]
        print(f"Truck {truck_id} has {len(truck['deliveries'])} active deliveries")
        for delivery_id in truck['deliveries']:
            delivery = routing_system.deliveries[delivery_id]
            print(f"  Delivery {delivery_id}: {delivery['weight']}kg from {delivery['pickup']} to {delivery['dropoff']}")
    
    success = routing_system.handle_truck_breakdown(truck_id)
    print(f"Emergency rerouting {'successful' if success else 'failed'}")
    
    # Report reassignment results
    for delivery_id in routing_system.deliveries:
        delivery = routing_system.deliveries[delivery_id]
        if delivery['status'] == 'in_progress':
            print(f"Delivery {delivery_id} is now assigned to truck {delivery['assigned_truck']}")
    
    routing_system.visualize_routes()
    
    print("\nTest completed. Check dynamic_routes.html for visualizations.")

if __name__ == "__main__":
    main() 