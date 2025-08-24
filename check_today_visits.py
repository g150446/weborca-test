#!/usr/bin/env python3
import pyodbc

# Connect to the database
connection_string = "DRIVER={PostgreSQL Unicode};SERVER=100.126.66.97;PORT=5432;DATABASE=orca;UID=orca;PWD=orca;"

try:
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    
    # Get today's date in YYYYMMDD format
    cursor.execute("SELECT TO_CHAR(CURRENT_DATE, 'YYYYMMDD');")
    today = cursor.fetchone()[0]
    print(f"Today's date: {today}")
    
    # Check today's visits
    print(f"\n=== Visits for {today} ===")
    cursor.execute("""
        SELECT 
            u.ukeymd,
            u.uketime,
            u.ptid,
            u.name,
            u.sryka,
            p.name as full_name,
            p.kananame
        FROM tbl_uketuke u
        LEFT JOIN tbl_ptinf p ON u.ptid = p.ptid
        WHERE u.ukeymd = ? 
        AND u.name IS NOT NULL 
        AND u.name != ''
        AND u.hospnum = 1
        ORDER BY u.uketime;
    """, (today,))
    
    today_visits = cursor.fetchall()
    
    if today_visits:
        for visit in today_visits:
            ukeymd, uketime, ptid, name, sryka, full_name, kananame = visit
            time_str = f"{uketime[:2]}:{uketime[2:4]}:{uketime[4:6]}" if uketime and len(uketime) >= 6 else uketime or "未設定"
            print(f"Patient ID: {ptid}, Name: {name or full_name}, Time: {time_str}, Dept: {sryka}")
    else:
        print("No visits found for today")
    
    # Check recent visits (last 7 days) for testing
    print(f"\n=== Recent visits (last 7 days) ===")
    cursor.execute("""
        SELECT 
            u.ukeymd,
            u.uketime,
            u.ptid,
            u.name,
            u.sryka,
            p.name as full_name,
            p.kananame
        FROM tbl_uketuke u
        LEFT JOIN tbl_ptinf p ON u.ptid = p.ptid
        WHERE u.ukeymd >= TO_CHAR(CURRENT_DATE - INTERVAL '7 days', 'YYYYMMDD')
        AND u.name IS NOT NULL 
        AND u.name != ''
        AND u.hospnum = 1
        ORDER BY u.ukeymd DESC, u.uketime DESC;
    """)
    
    recent_visits = cursor.fetchall()
    
    if recent_visits:
        for visit in recent_visits:
            ukeymd, uketime, ptid, name, sryka, full_name, kananame = visit
            date_str = f"{ukeymd[:4]}/{ukeymd[4:6]}/{ukeymd[6:8]}" if ukeymd else "未設定"
            time_str = f"{uketime[:2]}:{uketime[2:4]}:{uketime[4:6]}" if uketime and len(uketime) >= 6 else uketime or "未設定"
            print(f"Date: {date_str}, Time: {time_str}, Patient: {name or full_name}")
    else:
        print("No recent visits found")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"Error: {e}")