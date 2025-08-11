#!/usr/bin/env python3
import pyodbc

# Connect to the database
connection_string = "DRIVER={PostgreSQL Unicode};SERVER=localhost;PORT=5432;DATABASE=orca;UID=orca;PWD=orca;"

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    
    # Look for visit/appointment related tables
    print("=== Looking for visit/appointment tables ===")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND (table_name LIKE '%uketuke%' OR 
             table_name LIKE '%visit%' OR 
             table_name LIKE '%jyurrk%' OR
             table_name LIKE '%sryact%' OR
             table_name LIKE '%nyukin%')
        ORDER BY table_name;
    """)
    
    visit_tables = cursor.fetchall()
    for table in visit_tables:
        print(f"- {table[0]}")
    
    # Examine tbl_uketuke (reception/visit table)
    if visit_tables:
        print("\n=== Structure of tbl_uketuke ===")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tbl_uketuke' 
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]} ({col[1]})")
        
        # Check sample data
        print("\n=== Sample data from tbl_uketuke (first 3 records) ===")
        cursor.execute("SELECT * FROM tbl_uketuke LIMIT 3;")
        sample_data = cursor.fetchall()
        
        if sample_data:
            # Get column names
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'tbl_uketuke' 
                ORDER BY ordinal_position;
            """)
            col_names = [row[0] for row in cursor.fetchall()]
            
            for i, record in enumerate(sample_data, 1):
                print(f"\n--- Record {i} ---")
                for j, value in enumerate(record):
                    if j < len(col_names):
                        print(f"  {col_names[j]}: {value}")
        else:
            print("No sample data found in tbl_uketuke")
    
    # Also check tbl_jyurrk (visit records)
    print("\n=== Structure of tbl_jyurrk ===")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'tbl_jyurrk' 
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[0]} ({col[1]})")
    
    # Check for today's date format in the database
    print("\n=== Checking date formats ===")
    cursor.execute("SELECT CURRENT_DATE, TO_CHAR(CURRENT_DATE, 'YYYYMMDD');")
    today_info = cursor.fetchone()
    print(f"Current date: {today_info[0]}")
    print(f"YYYYMMDD format: {today_info[1]}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")