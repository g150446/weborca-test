#!/usr/bin/env python3
import pyodbc

# Connect to the database
connection_string = "DRIVER={PostgreSQL Unicode};SERVER=100.126.66.97;PORT=5432;DATABASE=orca;UID=orca;PWD=orca;"

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    
    # Examine tbl_ptinf (likely main patient info table)
    print("=== Structure of tbl_ptinf ===")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'tbl_ptinf' 
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]} ({col[1]})")
    
    # Check a few sample records to understand the data structure
    print("\n=== Sample data from tbl_ptinf (first 3 records) ===")
    cursor.execute("SELECT * FROM tbl_ptinf LIMIT 3;")
    sample_data = cursor.fetchall()
    
    if sample_data:
        # Get column names
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tbl_ptinf' 
            ORDER BY ordinal_position;
        """)
        col_names = [row[0] for row in cursor.fetchall()]
        
        for i, record in enumerate(sample_data, 1):
            print(f"\n--- Record {i} ---")
            for j, value in enumerate(record):
                if j < len(col_names):
                    print(f"  {col_names[j]}: {value}")
    else:
        print("No sample data found")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")