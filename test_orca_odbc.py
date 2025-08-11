#!/usr/bin/env python3
"""
Web ORCA PostgreSQL ODBC Connection Test Script

This script tests the ODBC connection to the PostgreSQL database used by Web ORCA.
It attempts to connect using both ANSI and Unicode PostgreSQL ODBC drivers.
"""

import pyodbc
import sys
from typing import Optional, Dict, Any


def test_connection(connection_string: str, driver_name: str) -> Optional[Dict[str, Any]]:
    """
    Test ODBC connection with the given connection string.
    
    Args:
        connection_string: The ODBC connection string
        driver_name: Name of the ODBC driver being tested
        
    Returns:
        Dictionary with connection test results or None if failed
    """
    try:
        print(f"\n=== Testing {driver_name} Driver ===")
        print(f"Connection string: {connection_string}")
        
        # Attempt to connect
        connection = pyodbc.connect(connection_string, timeout=10)
        
        # Get basic connection info
        cursor = connection.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Get database name
        cursor.execute("SELECT current_database();")
        database = cursor.fetchone()[0]
        
        # Get current user
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()[0]
        
        # Get server encoding
        cursor.execute("SHOW server_encoding;")
        encoding = cursor.fetchone()[0]
        
        result = {
            'success': True,
            'driver': driver_name,
            'version': version,
            'database': database,
            'user': user,
            'encoding': encoding,
            'connection': connection
        }
        
        print(f"✓ Connection successful!")
        print(f"  Database: {database}")
        print(f"  User: {user}")
        print(f"  PostgreSQL Version: {version}")
        print(f"  Encoding: {encoding}")
        
        cursor.close()
        connection.close()
        
        return result
        
    except pyodbc.Error as e:
        print(f"✗ Connection failed: {e}")
        return None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return None


def list_available_drivers():
    """List all available ODBC drivers on the system."""
    print("=== Available ODBC Drivers ===")
    drivers = pyodbc.drivers()
    for i, driver in enumerate(drivers, 1):
        print(f"{i}. {driver}")
    return drivers


def test_orca_database():
    """Test connection to Web ORCA PostgreSQL database."""
    print("Web ORCA PostgreSQL ODBC Connection Test")
    print("=" * 50)
    
    # List available drivers
    drivers = list_available_drivers()
    
    # Common Web ORCA database connection parameters
    # These are typical defaults - you may need to adjust based on your setup
    connection_params = {
        'server': 'localhost',
        'port': '5432',
        'database': 'orca',  # Common ORCA database name
        'uid': 'orca',       # Common ORCA user
        'pwd': 'orca',       # Default password - should be changed in production
    }
    
    # Alternative connection parameters to try
    alternative_params = [
        {'database': 'receipt', 'uid': 'receipt', 'pwd': 'receipt'},
        {'database': 'weborca', 'uid': 'weborca', 'pwd': 'weborca'},
        {'database': 'postgres', 'uid': 'postgres', 'pwd': ''},
    ]
    
    # Test with PostgreSQL ANSI driver
    ansi_connection_string = (
        f"DRIVER={{PostgreSQL ANSI}};"
        f"SERVER={connection_params['server']};"
        f"PORT={connection_params['port']};"
        f"DATABASE={connection_params['database']};"
        f"UID={connection_params['uid']};"
        f"PWD={connection_params['pwd']};"
    )
    
    result_ansi = test_connection(ansi_connection_string, "PostgreSQL ANSI")
    
    # Test with PostgreSQL Unicode driver if ANSI failed
    if not result_ansi:
        unicode_connection_string = (
            f"DRIVER={{PostgreSQL Unicode}};"
            f"SERVER={connection_params['server']};"
            f"PORT={connection_params['port']};"
            f"DATABASE={connection_params['database']};"
            f"UID={connection_params['uid']};"
            f"PWD={connection_params['pwd']};"
        )
        
        result_unicode = test_connection(unicode_connection_string, "PostgreSQL Unicode")
        
        # If both failed, try alternative parameters
        if not result_unicode:
            print("\n=== Trying Alternative Connection Parameters ===")
            for alt_params in alternative_params:
                print(f"\nTrying database: {alt_params['database']}, user: {alt_params['uid']}")
                
                alt_connection_string = (
                    f"DRIVER={{PostgreSQL ANSI}};"
                    f"SERVER={connection_params['server']};"
                    f"PORT={connection_params['port']};"
                    f"DATABASE={alt_params['database']};"
                    f"UID={alt_params['uid']};"
                    f"PWD={alt_params['pwd']};"
                )
                
                result = test_connection(alt_connection_string, f"PostgreSQL ANSI ({alt_params['database']})")
                if result:
                    break
    
    print("\n=== Connection Test Summary ===")
    print("If all connections failed, check:")
    print("1. PostgreSQL is running and accepting connections")
    print("2. Database name, username, and password are correct")
    print("3. User has proper permissions to access the database")
    print("4. ODBC drivers are properly installed")
    print("5. Firewall settings allow database connections")


def list_patients():
    """List all patients registered in the Web ORCA database."""
    print("\n=== Patient List ===")
    
    # Use the working connection parameters
    connection_string = (
        f"DRIVER={{PostgreSQL Unicode}};"
        f"SERVER=localhost;"
        f"PORT=5432;"
        f"DATABASE=orca;"
        f"UID=orca;"
        f"PWD=orca;"
    )
    
    try:
        connection = pyodbc.connect(connection_string, timeout=10)
        cursor = connection.cursor()
        
        # Query patient information
        query = """
            SELECT 
                ptid,
                name,
                kananame,
                CASE 
                    WHEN sex = '1' THEN '男性'
                    WHEN sex = '2' THEN '女性'
                    ELSE '不明'
                END as gender,
                CASE 
                    WHEN birthday IS NOT NULL AND birthday != '' THEN
                        SUBSTRING(birthday, 1, 4) || '年' || 
                        SUBSTRING(birthday, 5, 2) || '月' || 
                        SUBSTRING(birthday, 7, 2) || '日'
                    ELSE '生年月日不明'
                END as birth_date,
                CASE 
                    WHEN deathkbn IS NOT NULL AND deathkbn != ' ' THEN '死亡'
                    ELSE '生存'
                END as status,
                creymd as registration_date
            FROM tbl_ptinf 
            WHERE hospnum = 1
            ORDER BY ptid;
        """
        
        cursor.execute(query)
        patients = cursor.fetchall()
        
        if not patients:
            print("患者データが見つかりませんでした。")
            return
        
        print(f"登録患者数: {len(patients)}名\n")
        print("=" * 80)
        print(f"{'ID':>4} | {'患者名':^20} | {'フリガナ':^20} | {'性別':^6} | {'生年月日':^12} | {'状態':^6}")
        print("=" * 80)
        
        for patient in patients:
            ptid = patient[0]
            name = patient[1] or "名前なし"
            kananame = patient[2] or "フリガナなし"
            gender = patient[3]
            birth_date = patient[4]
            status = patient[5]
            
            # Truncate long names for display
            if len(name) > 18:
                name = name[:15] + "..."
            if len(kananame) > 18:
                kananame = kananame[:15] + "..."
            
            print(f"{ptid:>4} | {name:^20} | {kananame:^20} | {gender:^6} | {birth_date:^12} | {status:^6}")
        
        print("=" * 80)
        
        # Show statistics
        print(f"\n=== 統計情報 ===")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_patients,
                COUNT(CASE WHEN sex = '1' THEN 1 END) as male_count,
                COUNT(CASE WHEN sex = '2' THEN 1 END) as female_count,
                COUNT(CASE WHEN deathkbn IS NOT NULL AND deathkbn != ' ' THEN 1 END) as deceased_count
            FROM tbl_ptinf 
            WHERE hospnum = 1;
        """)
        
        stats = cursor.fetchone()
        if stats:
            print(f"総患者数: {stats[0]}名")
            print(f"男性: {stats[1]}名")
            print(f"女性: {stats[2]}名")
            print(f"死亡: {stats[3]}名")
        
        cursor.close()
        connection.close()
        
    except pyodbc.Error as e:
        print(f"✗ データベース接続エラー: {e}")
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")


def search_patients():
    """Search for patients by name."""
    print("\n=== 患者検索 ===")
    
    search_term = input("患者名またはフリガナを入力してください: ").strip()
    if not search_term:
        print("検索語を入力してください。")
        return
    
    connection_string = (
        f"DRIVER={{PostgreSQL Unicode}};"
        f"SERVER=localhost;"
        f"PORT=5432;"
        f"DATABASE=orca;"
        f"UID=orca;"
        f"PWD=orca;"
    )
    
    try:
        connection = pyodbc.connect(connection_string, timeout=10)
        cursor = connection.cursor()
        
        # Search query with LIKE for partial matches
        query = """
            SELECT 
                ptid,
                name,
                kananame,
                CASE 
                    WHEN sex = '1' THEN '男性'
                    WHEN sex = '2' THEN '女性'
                    ELSE '不明'
                END as gender,
                CASE 
                    WHEN birthday IS NOT NULL AND birthday != '' THEN
                        SUBSTRING(birthday, 1, 4) || '年' || 
                        SUBSTRING(birthday, 5, 2) || '月' || 
                        SUBSTRING(birthday, 7, 2) || '日'
                    ELSE '生年月日不明'
                END as birth_date,
                home_tel1,
                home_adrs
            FROM tbl_ptinf 
            WHERE hospnum = 1 
            AND (name LIKE ? OR kananame LIKE ?)
            ORDER BY ptid;
        """
        
        search_pattern = f"%{search_term}%"
        cursor.execute(query, (search_pattern, search_pattern))
        results = cursor.fetchall()
        
        if not results:
            print(f"「{search_term}」に一致する患者が見つかりませんでした。")
        else:
            print(f"検索結果: {len(results)}件\n")
            print("=" * 100)
            print(f"{'ID':>4} | {'患者名':^15} | {'フリガナ':^15} | {'性別':^6} | {'生年月日':^12} | {'電話番号':^15}")
            print("=" * 100)
            
            for patient in results:
                ptid = patient[0]
                name = patient[1] or "名前なし"
                kananame = patient[2] or "フリガナなし"
                gender = patient[3]
                birth_date = patient[4]
                phone = patient[5] or "未登録"
                
                # Truncate long fields for display
                if len(name) > 13:
                    name = name[:10] + "..."
                if len(kananame) > 13:
                    kananame = kananame[:10] + "..."
                if len(phone) > 13:
                    phone = phone[:10] + "..."
                
                print(f"{ptid:>4} | {name:^15} | {kananame:^15} | {gender:^6} | {birth_date:^12} | {phone:^15}")
            
            print("=" * 100)
        
        cursor.close()
        connection.close()
        
    except pyodbc.Error as e:
        print(f"✗ データベース接続エラー: {e}")
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")


def show_todays_visits():
    """Show patients who visited today and their visit times."""
    print("\n=== 本日の来院患者 ===")
    
    connection_string = (
        f"DRIVER={{PostgreSQL Unicode}};"
        f"SERVER=localhost;"
        f"PORT=5432;"
        f"DATABASE=orca;"
        f"UID=orca;"
        f"PWD=orca;"
    )
    
    try:
        connection = pyodbc.connect(connection_string, timeout=10)
        cursor = connection.cursor()
        
        # Get today's date in YYYYMMDD format
        cursor.execute("SELECT TO_CHAR(CURRENT_DATE, 'YYYYMMDD');")
        today = cursor.fetchone()[0]
        
        # Get today's visits
        query = """
            SELECT 
                u.ukeymd,
                u.uketime,
                u.ptid,
                u.name,
                u.sryka,
                p.name as full_name,
                p.kananame,
                p.sex,
                p.birthday
            FROM tbl_uketuke u
            LEFT JOIN tbl_ptinf p ON u.ptid = p.ptid
            WHERE u.ukeymd = ? 
            AND u.name IS NOT NULL 
            AND u.name != ''
            AND u.hospnum = 1
            ORDER BY u.uketime;
        """
        
        cursor.execute(query, (today,))
        visits = cursor.fetchall()
        
        if not visits:
            print(f"本日（{today[:4]}年{today[4:6]}月{today[6:8]}日）の来院患者はいません。")
            return
        
        print(f"本日（{today[:4]}年{today[4:6]}月{today[6:8]}日）の来院患者数: {len(visits)}名\n")
        print("=" * 90)
        print(f"{'来院時刻':^12} | {'患者ID':^8} | {'患者名':^20} | {'フリガナ':^18} | {'診療科':^8}")
        print("=" * 90)
        
        for visit in visits:
            ukeymd, uketime, ptid, name, sryka, full_name, kananame, sex, birthday = visit
            
            # Format time
            if uketime and len(uketime) >= 6:
                time_str = f"{uketime[:2]}:{uketime[2:4]}:{uketime[4:6]}"
            else:
                time_str = uketime or "未設定"
            
            # Use name from visit record, fallback to patient table
            patient_name = name or full_name or "名前なし"
            patient_kana = kananame or "フリガナなし"
            
            # Department mapping (common ORCA department codes)
            dept_map = {
                '01': '内科',
                '02': '外科', 
                '03': '小児科',
                '04': '産婦人科',
                '05': '眼科',
                '06': '耳鼻科',
                '07': '皮膚科',
                '08': '泌尿器科',
                '09': '整形外科',
                '10': '脳神経外科',
                '11': '呼吸器科',
                '12': '循環器科'
            }
            dept_name = dept_map.get(sryka, sryka or '未設定')
            
            # Truncate long names for display
            if len(patient_name) > 18:
                patient_name = patient_name[:15] + "..."
            if len(patient_kana) > 16:
                patient_kana = patient_kana[:13] + "..."
            
            print(f"{time_str:^12} | {ptid:^8} | {patient_name:^20} | {patient_kana:^18} | {dept_name:^8}")
        
        print("=" * 90)
        
        # Show department statistics
        print(f"\n=== 診療科別統計 ===")
        cursor.execute("""
            SELECT 
                u.sryka,
                COUNT(*) as visit_count
            FROM tbl_uketuke u
            WHERE u.ukeymd = ? 
            AND u.name IS NOT NULL 
            AND u.name != ''
            AND u.hospnum = 1
            GROUP BY u.sryka
            ORDER BY visit_count DESC;
        """, (today,))
        
        dept_stats = cursor.fetchall()
        if dept_stats:
            for dept, count in dept_stats:
                dept_map = {
                    '01': '内科', '02': '外科', '03': '小児科', '04': '産婦人科',
                    '05': '眼科', '06': '耳鼻科', '07': '皮膚科', '08': '泌尿器科',
                    '09': '整形外科', '10': '脳神経外科', '11': '呼吸器科', '12': '循環器科'
                }
                dept_name = dept_map.get(dept, dept or '不明')
                print(f"{dept_name}: {count}名")
        
        cursor.close()
        connection.close()
        
    except pyodbc.Error as e:
        print(f"✗ データベース接続エラー: {e}")
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")


def test_specific_connection():
    """Interactive function to test a specific connection."""
    print("\n=== Custom Connection Test ===")
    
    # Get connection parameters from user
    server = input("Enter server (default: localhost): ") or "localhost"
    port = input("Enter port (default: 5432): ") or "5432"
    database = input("Enter database name: ")
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    if not database or not username:
        print("Database name and username are required!")
        return
    
    # Choose driver
    print("\nAvailable PostgreSQL drivers:")
    print("1. PostgreSQL ANSI")
    print("2. PostgreSQL Unicode")
    choice = input("Choose driver (1 or 2, default: 1): ") or "1"
    
    driver = "PostgreSQL ANSI" if choice == "1" else "PostgreSQL Unicode"
    
    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"PORT={port};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
    )
    
    test_connection(connection_string, driver)


if __name__ == "__main__":
    try:
        # Check if pyodbc is available
        import pyodbc
        
        if len(sys.argv) > 1:
            if sys.argv[1] == "--interactive":
                test_specific_connection()
            elif sys.argv[1] == "--patients":
                list_patients()
            elif sys.argv[1] == "--search":
                search_patients()
            elif sys.argv[1] == "--today":
                show_todays_visits()
            elif sys.argv[1] == "--help":
                print("Web ORCA PostgreSQL ODBC Connection Test Script")
                print("\nUsage:")
                print("  python3 test_orca_odbc.py                - Test ODBC connection")
                print("  python3 test_orca_odbc.py --patients     - List all patients")
                print("  python3 test_orca_odbc.py --search       - Search patients by name")
                print("  python3 test_orca_odbc.py --today        - Show today's visits")
                print("  python3 test_orca_odbc.py --interactive  - Custom connection test")
                print("  python3 test_orca_odbc.py --help         - Show this help")
            else:
                print(f"Unknown option: {sys.argv[1]}")
                print("Use --help to see available options.")
        else:
            # Default: run connection test and show patient count
            test_orca_database()
            
            # After successful connection test, show patient summary
            print("\n" + "="*50)
            print("患者データの概要を表示しています...")
            
            connection_string = (
                f"DRIVER={{PostgreSQL Unicode}};"
                f"SERVER=localhost;"
                f"PORT=5432;"
                f"DATABASE=orca;"
                f"UID=orca;"
                f"PWD=orca;"
            )
            
            try:
                connection = pyodbc.connect(connection_string, timeout=10)
                cursor = connection.cursor()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_patients,
                        COUNT(CASE WHEN sex = '1' THEN 1 END) as male_count,
                        COUNT(CASE WHEN sex = '2' THEN 1 END) as female_count
                    FROM tbl_ptinf 
                    WHERE hospnum = 1;
                """)
                
                stats = cursor.fetchone()
                if stats and stats[0] > 0:
                    print(f"\n=== 患者データ概要 ===")
                    print(f"登録患者数: {stats[0]}名")
                    print(f"男性: {stats[1]}名, 女性: {stats[2]}名")
                    
                    # Show today's visit count
                    cursor.execute("SELECT TO_CHAR(CURRENT_DATE, 'YYYYMMDD');")
                    today = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM tbl_uketuke 
                        WHERE ukeymd = ? 
                        AND name IS NOT NULL 
                        AND name != ''
                        AND hospnum = 1;
                    """, (today,))
                    
                    today_visits = cursor.fetchone()[0]
                    print(f"本日の来院患者数: {today_visits}名")
                    
                    print(f"\n患者一覧を表示するには: python3 {sys.argv[0]} --patients")
                    print(f"患者を検索するには: python3 {sys.argv[0]} --search")
                    print(f"本日の来院患者を表示するには: python3 {sys.argv[0]} --today")
                else:
                    print("患者データが登録されていません。")
                
                cursor.close()
                connection.close()
                
            except Exception as e:
                print(f"患者データの取得に失敗しました: {e}")
            
    except ImportError:
        print("Error: pyodbc module is not installed.")
        print("Please install it using: pip install pyodbc")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)