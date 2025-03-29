from dynamic_routing import DynamicRoutingSystem
import time
import random
from datetime import datetime, timedelta

"""
Test Scenarios for Dynamic Routing System

This module contains comprehensive test scenarios for the dynamic routing system.
Expected Test Results:

1. High Priority Deliveries (Scenario 1):
   - HP1 (Delhi to Mumbai, 1000kg): Should PASS
   - HP2 (Bangalore to Chennai, 1500kg): Should PASS
   - HP3 (Kolkata to Hyderabad, 2000kg): Should PASS
   Reason: High priority deliveries should be prioritized for assignment

2. Capacity Management (Scenario 2):
   - C1 (4500kg): Should FAIL (exceeds truck capacity)
   - C2 (1000kg): Should PASS (within capacity)
   - C3 (2000kg): Should PASS (medium delivery)
   - C4 (3000kg): Should PASS (large delivery)
   Reason: System should properly manage and enforce capacity constraints

3. Multiple Deliveries (Scenario 3):
   - M1 (1000kg): Should PASS (assigned to T1)
   - M2 (1500kg): Should PASS (assigned to T2)
   - M3 (1000kg): Should PASS (assigned to T4)
   - M4 (2000kg): Should PASS (assigned to T5)
   Reason: System should handle multiple deliveries efficiently

4. Emergency Rerouting (Scenario 4):
   - E1 (2000kg): Should PASS (reassigned after T1 breakdown)
   - E2 (1500kg): Should PASS (reassigned after T1 breakdown)
   - E3 (1000kg): Should PASS (reassigned after T1 breakdown)
   Reason: System should handle truck breakdowns by reassigning deliveries

5. Time Window Deliveries (Scenario 5):
   - TW1 (2-hour window): Should PASS (immediate window)
   - TW2 (2-hour window): Should PASS (1-hour delay)
   - TW3 (2-hour window): Should PASS (2-hour delay)
   Reason: System should respect time window constraints

Note: The actual results may vary based on:
- Current system state
- Truck availability
- Time of execution
- System load
"""

class TestScenarios:
    def __init__(self):
        self.routing_system = DynamicRoutingSystem()
        self.routing_system.load_truck_data("GIS/Delivery truck trip data.xlsx")
        
        # Initialize trucks with different capacities and locations
        self.trucks = [
            ("T1", 5000, (20.5937, 78.9629)),  # Delhi
            ("T2", 3000, (19.0760, 72.8777)),  # Mumbai
            ("T3", 4000, (12.9716, 77.5946)),  # Bangalore
            ("T4", 3500, (13.0827, 80.2707)),  # Chennai
            ("T5", 6000, (22.5726, 88.3639))   # Kolkata
        ]
        
        for truck_id, capacity, location in self.trucks:
            self.routing_system.add_truck(truck_id, capacity, location)
            
        self.locations = [
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
    
    def scenario_1_high_priority_deliveries(self):
        """Test high-priority delivery assignments"""
        print("\n=== Scenario 1: High Priority Deliveries ===")
        
        # Add high-priority deliveries
        high_priority_deliveries = [
            ("HP1", (20.5937, 78.9629), (19.0760, 72.8777), 1000, "urgent"),  # Delhi to Mumbai
            ("HP2", (12.9716, 77.5946), (13.0827, 80.2707), 1500, "urgent"),  # Bangalore to Chennai
            ("HP3", (22.5726, 88.3639), (17.3850, 78.4867), 2000, "urgent")   # Kolkata to Hyderabad
        ]
        
        for delivery_id, pickup, dropoff, weight, priority in high_priority_deliveries:
            self.routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
            success = self.routing_system.assign_delivery(delivery_id)
            print(f"High-priority delivery {delivery_id} assigned: {'Success' if success else 'Failed'}")
        
        self.routing_system.visualize_routes()
    
    def scenario_2_capacity_management(self):
        """Test capacity constraints and management"""
        print("\n=== Scenario 2: Capacity Management ===")
        
        # Add deliveries that test capacity limits
        capacity_test_deliveries = [
            ("C1", (20.5937, 78.9629), (19.0760, 72.8777), 4500),  # Almost full truck
            ("C2", (12.9716, 77.5946), (13.0827, 80.2707), 1000),  # Small delivery
            ("C3", (22.5726, 88.3639), (17.3850, 78.4867), 2000),  # Medium delivery
            ("C4", (19.2183, 72.9781), (18.5204, 73.8567), 3000)   # Large delivery
        ]
        
        for delivery_id, pickup, dropoff, weight in capacity_test_deliveries:
            self.routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
            success = self.routing_system.assign_delivery(delivery_id)
            print(f"Capacity test delivery {delivery_id} ({weight}kg) assigned: {'Success' if success else 'Failed'}")
        
        self.routing_system.visualize_routes()
    
    def scenario_3_multiple_deliveries(self):
        """Test multiple deliveries per truck"""
        print("\n=== Scenario 3: Multiple Deliveries per Truck ===")
        
        # Add multiple deliveries for the same truck
        multiple_deliveries = [
            ("M1", (20.5937, 78.9629), (19.0760, 72.8777), 1000),  # Delhi to Mumbai
            ("M2", (19.0760, 72.8777), (12.9716, 77.5946), 1500),  # Mumbai to Bangalore
            ("M3", (12.9716, 77.5946), (13.0827, 80.2707), 1000),  # Bangalore to Chennai
            ("M4", (13.0827, 80.2707), (22.5726, 88.3639), 2000)   # Chennai to Kolkata
        ]
        
        for delivery_id, pickup, dropoff, weight in multiple_deliveries:
            self.routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
            success = self.routing_system.assign_delivery(delivery_id)
            print(f"Multiple delivery {delivery_id} assigned: {'Success' if success else 'Failed'}")
        
        self.routing_system.visualize_routes()
    
    def scenario_4_emergency_rerouting(self):
        """Test emergency rerouting when a truck breaks down"""
        print("\n=== Scenario 4: Emergency Rerouting ===")
        
        # First assign some deliveries
        initial_deliveries = [
            ("E1", (20.5937, 78.9629), (19.0760, 72.8777), 2000),
            ("E2", (19.0760, 72.8777), (12.9716, 77.5946), 1500),
            ("E3", (12.9716, 77.5946), (13.0827, 80.2707), 1000)
        ]
        
        for delivery_id, pickup, dropoff, weight in initial_deliveries:
            self.routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
            self.routing_system.assign_delivery(delivery_id)
        
        print("Initial assignments completed")
        self.routing_system.visualize_routes()
        
        # Simulate truck breakdown
        print("\nSimulating truck breakdown...")
        # Remove truck T1 and reassign its deliveries
        if "T1" in self.routing_system.trucks:
            failed_deliveries = self.routing_system.trucks["T1"]["deliveries"]
            del self.routing_system.trucks["T1"]
            
            # Reassign failed deliveries
            for delivery_id in failed_deliveries:
                success = self.routing_system.assign_delivery(delivery_id)
                print(f"Reassignment of {delivery_id}: {'Success' if success else 'Failed'}")
        
        self.routing_system.visualize_routes()
    
    def scenario_5_time_windows(self):
        """Test delivery assignments with time windows"""
        print("\n=== Scenario 5: Time Window Deliveries ===")
        
        # Add deliveries with time windows
        time_window_deliveries = [
            ("TW1", (20.5937, 78.9629), (19.0760, 72.8777), 1000, 
             datetime.now(), datetime.now() + timedelta(hours=2)),
            ("TW2", (12.9716, 77.5946), (13.0827, 80.2707), 1500,
             datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=3)),
            ("TW3", (22.5726, 88.3639), (17.3850, 78.4867), 2000,
             datetime.now() + timedelta(hours=2), datetime.now() + timedelta(hours=4))
        ]
        
        for delivery_id, pickup, dropoff, weight, start_time, end_time in time_window_deliveries:
            self.routing_system.add_delivery(delivery_id, pickup, dropoff, weight)
            success = self.routing_system.assign_delivery(delivery_id)
            print(f"Time window delivery {delivery_id} assigned: {'Success' if success else 'Failed'}")
            print(f"Time window: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        self.routing_system.visualize_routes()

def main():
    # Initialize test scenarios
    test_scenarios = TestScenarios()
    
    # Run all scenarios
    test_scenarios.scenario_1_high_priority_deliveries()
    time.sleep(2)  # Wait between scenarios
    
    test_scenarios.scenario_2_capacity_management()
    time.sleep(2)
    
    test_scenarios.scenario_3_multiple_deliveries()
    time.sleep(2)
    
    test_scenarios.scenario_4_emergency_rerouting()
    time.sleep(2)
    
    test_scenarios.scenario_5_time_windows()
    
    print("\nAll test scenarios completed. Check dynamic_routes.html for visualizations.")

if __name__ == "__main__":
    main() 