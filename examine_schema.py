#!/usr/bin/env python3
import pyodbc

# Connect to the database
connection_string = "DRIVER={PostgreSQL Unicode};SERVER=localhost;PORT=5432;DATABASE=orca;UID=orca;PWD=orca;"

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    
    # Get all table names
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print("=== Database Tables ===")
    for table in tables:
        print(f"- {table[0]}")
    
    # Look for patient-related tables
    print("\n=== Potential Patient Tables ===")
    patient_tables = [t[0] for t in tables if any(keyword in t[0].lower() for keyword in ['patient', 'ptnt', 'kanja', '患者'])]
    for table in patient_tables:
        print(f"- {table}")
    
    # If we found patient tables, examine their structure
    if patient_tables:
        for table in patient_tables[:3]:  # Examine first 3 patient tables
            print(f"\n=== Structure of {table} ===")
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            for col in columns:
                print(f"  {col[0]} ({col[1]})")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")