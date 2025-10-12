#!/usr/bin/env python3
"""
FixMyHyd Demo Data Script
Adds sample data to the database for demonstration purposes
"""

import sqlite3
import random
from datetime import datetime, timedelta
from app import get_db_connection, hash_password

def add_demo_data():
    """Add sample data to the database"""
    print("Adding demo data to FixMyHyd...")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Sample users
    demo_users = [
        ("Rajesh Kumar", "rajesh@example.com", "rajesh123", "+91-9876543210"),
        ("Priya Sharma", "priya@example.com", "priya123", "+91-9876543211"),
        ("Amit Patel", "amit@example.com", "amit123", "+91-9876543212"),
        ("Sneha Reddy", "sneha@example.com", "sneha123", "+91-9876543213"),
        ("Vikram Singh", "vikram@example.com", "vikram123", "+91-9876543214"),
    ]
    
    print("Adding demo users...")
    for name, email, password, phone in demo_users:
        try:
            password_hash = hash_password(password)
            c.execute('''
                INSERT OR IGNORE INTO users (name, email, password_hash, phone)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, phone))
        except sqlite3.Error:
            pass  # User might already exist
    
    # Sample complaints
    complaint_templates = [
        {
            "category": "Open Garbage Dump",
            "subject": "Large garbage dump near metro station",
            "description": "There is a huge pile of garbage accumulating near the metro station entrance. It's causing bad smell and attracting stray animals.",
            "location": "Near HITEC City Metro Station",
            "zone": "Madhapur",
            "priority": "High"
        },
        {
            "category": "Pothole/Damaged Road",
            "subject": "Deep pothole on main road",
            "description": "There's a very deep pothole on the main road that's causing traffic jams and vehicle damage. It's been there for weeks.",
            "location": "Road No. 12, Banjara Hills",
            "zone": "Banjar Hills",
            "priority": "High"
        },
        {
            "category": "Sewage Leak/Overflow",
            "subject": "Sewage water overflowing on street",
            "description": "Sewage water is overflowing from a manhole and spreading across the street. It's unhygienic and dangerous.",
            "location": "Near Jubilee Hills Check Post",
            "zone": "Jubilee Hills",
            "priority": "High"
        },
        {
            "category": "Damaged Electrical Infrastructure",
            "subject": "Broken street light causing darkness",
            "description": "Street light is broken and the area is completely dark at night. It's unsafe for pedestrians and vehicles.",
            "location": "Near Gachibowli Stadium",
            "zone": "Gachibowli",
            "priority": "Medium"
        },
        {
            "category": "Water Logging",
            "subject": "Water logging after rain",
            "description": "The road gets completely waterlogged even after light rain. It's difficult for vehicles to pass through.",
            "location": "Near Kondapur Main Road",
            "zone": "Kondapur",
            "priority": "Medium"
        },
        {
            "category": "Stray Animals",
            "subject": "Aggressive stray dogs in the area",
            "description": "There are several aggressive stray dogs in the area that are scaring residents and children. Need immediate attention.",
            "location": "Near Kukatpally Bus Stand",
            "zone": "Kukatpally",
            "priority": "Medium"
        },
        {
            "category": "Fallen Tree",
            "subject": "Tree branch fallen on road",
            "description": "A large tree branch has fallen on the road and is blocking traffic. It's also a safety hazard.",
            "location": "Near Secunderabad Railway Station",
            "zone": "Secunderabad",
            "priority": "High"
        },
        {
            "category": "Open Garbage Dump",
            "subject": "Garbage not being collected regularly",
            "description": "Garbage is not being collected regularly in our area. It's piling up and causing health issues.",
            "location": "Near Malakpet Market",
            "zone": "Malakpet",
            "priority": "Medium"
        }
    ]
    
    statuses = ["Submitted", "In Progress", "Resolved", "Closed"]
    
    print("Adding demo complaints...")
    for i, template in enumerate(complaint_templates):
        # Get random user
        user = c.execute('SELECT id FROM users ORDER BY RANDOM() LIMIT 1').fetchone()
        if not user:
            continue
            
        # Create GHMC ID
        ghmc_id = f"GHMC/HYD/{int(datetime.now().timestamp()) + i}"
        
        # Random status
        status = random.choice(statuses)
        
        # Random dates
        days_ago = random.randint(1, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        updated_at = created_at + timedelta(days=random.randint(0, days_ago))
        
        # Random GPS coordinates (Hyderabad area)
        gps_lat = 17.3850 + random.uniform(-0.1, 0.1)
        gps_lng = 78.4867 + random.uniform(-0.1, 0.1)
        
        try:
            c.execute('''
                INSERT INTO complaints 
                (ghmc_id, category, priority, subject, description, location, zone, 
                 gps_lat, gps_lng, status, submitted_by, user_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ghmc_id, template["category"], template["priority"], template["subject"],
                template["description"], template["location"], template["zone"],
                gps_lat, gps_lng, status, "Citizen", user[0], created_at, updated_at
            ))
            
            # Add status history
            if status != "Submitted":
                c.execute('''
                    INSERT INTO status_history 
                    (complaint_id, old_status, new_status, changed_by, comments, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    c.lastrowid, "Submitted", status, "Admin", 
                    f"Status updated to {status}", updated_at
                ))
                
        except sqlite3.Error as e:
            print(f"Error adding complaint {i+1}: {e}")
    
    conn.commit()
    conn.close()
    
    print("Demo data added successfully!")
    print("You can now see sample complaints in the admin dashboard")
    print("Demo users created (all passwords are 'user123'):")
    for name, email, _, _ in demo_users:
        print(f"   - {name} ({email})")

if __name__ == '__main__':
    add_demo_data()
