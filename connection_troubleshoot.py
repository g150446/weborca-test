#!/usr/bin/env python3
"""
PostgreSQL Connection Troubleshooting Tool
This script helps diagnose and resolve pg_hba.conf authentication issues.
"""

import pyodbc
import sys
from typing import List, Dict, Any

def test_connection_with_ssl_modes(server: str, port: str, database: str, user: str, password: str) -> Dict[str, Any]:
    """Test connection with different SSL modes."""
    
    ssl_modes = [
        ('disable', 'No SSL encryption'),
        ('allow', 'SSL if server prefers it'),
        ('prefer', 'SSL preferred but optional'),
        ('require', 'SSL required'),
    ]
    
    print(f"\n=== Testing connection to {database}@{server} as {user} ===")
    print(f"Your client IP appears to be: 100.89.18.15")
    
    for ssl_mode, description in ssl_modes:
        print(f"\nTrying SSL Mode: {ssl_mode} ({description})")
        
        connection_string = (
            f"DRIVER={{PostgreSQL Unicode}};"
            f"SERVER={server};"
            f"PORT={port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"SSLMode={ssl_mode};"
        )
        
        try:
            print(f"Connection string: {connection_string}")
            connection = pyodbc.connect(connection_string, timeout=10)
            
            # Test basic query
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            print(f"✓ SUCCESS with SSL mode: {ssl_mode}")
            print(f"  PostgreSQL Version: {version}")
            return {
                'success': True,
                'ssl_mode': ssl_mode,
                'version': version
            }
            
        except pyodbc.Error as e:
            error_msg = str(e)
            print(f"✗ FAILED with SSL mode: {ssl_mode}")
            print(f"  Error: {error_msg}")
            
            # Analyze the error
            if "pg_hba.conf entry" in error_msg:
                if "100.89.18.15" in error_msg:
                    print(f"  → Authentication issue: Your IP (100.89.18.15) is not allowed")
                    if "SSL encryption" in error_msg:
                        print(f"  → Server requires SSL but your IP is not in pg_hba.conf for SSL connections")
                    elif "no encryption" in error_msg:
                        print(f"  → Server allows non-SSL but your IP is not in pg_hba.conf")
            elif "authentication failed" in error_msg:
                print(f"  → Wrong username/password")
            elif "database" in error_msg and "does not exist" in error_msg:
                print(f"  → Database '{database}' does not exist")
    
    return {'success': False}

def generate_pg_hba_entries(databases: List[str], users: List[str], client_ip: str = "100.89.18.15") -> str:
    """Generate pg_hba.conf entries for the client."""
    
    entries = []
    entries.append("# Add these lines to pg_hba.conf on the PostgreSQL server")
    entries.append("# (Replace /32 with appropriate subnet if needed)")
    entries.append("")
    
    for db in databases:
        for user in users:
            # SSL connection
            entries.append(f"hostssl    {db:<12} {user:<12} {client_ip}/32        md5")
            # Non-SSL connection (if SSL is not required)
            entries.append(f"host       {db:<12} {user:<12} {client_ip}/32        md5")
    
    entries.append("")
    entries.append("# After adding these lines:")
    entries.append("# 1. Save the pg_hba.conf file")
    entries.append("# 2. Restart PostgreSQL or run: SELECT pg_reload_conf();")
    entries.append("# 3. Test the connection again")
    
    return "\n".join(entries)

def main():
    print("PostgreSQL Connection Troubleshooting Tool")
    print("=" * 60)
    
    # Test parameters
    server = "100.126.66.97"
    port = "5432"
    
    test_configs = [
        {'database': 'orca', 'user': 'orca', 'password': 'orca'},
        {'database': 'receipt', 'user': 'receipt', 'password': 'receipt'},
        {'database': 'weborca', 'user': 'weborca', 'password': 'weborca'},
        {'database': 'postgres', 'user': 'postgres', 'password': ''},
    ]
    
    successful_connections = []
    
    for config in test_configs:
        result = test_connection_with_ssl_modes(
            server, port, 
            config['database'], 
            config['user'], 
            config['password']
        )
        
        if result['success']:
            successful_connections.append(config)
    
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING SUMMARY")
    print("=" * 60)
    
    if successful_connections:
        print(f"✓ Successfully connected to {len(successful_connections)} database(s)")
        for conn in successful_connections:
            print(f"  - {conn['database']} as {conn['user']}")
    else:
        print("✗ No successful connections")
        print("\nROOT CAUSE:")
        print("The PostgreSQL server's pg_hba.conf file does not allow")
        print("connections from your IP address (100.89.18.15).")
        
        print("\n" + "=" * 60)
        print("SOLUTION FOR DATABASE ADMINISTRATOR")
        print("=" * 60)
        
        databases = [config['database'] for config in test_configs]
        users = [config['user'] for config in test_configs]
        
        pg_hba_config = generate_pg_hba_entries(databases, users)
        print(pg_hba_config)
        
        print("\n" + "=" * 60)
        print("ALTERNATIVE SOLUTIONS")
        print("=" * 60)
        print("1. VPN/Tunnel: Connect through a VPN that routes through an allowed IP")
        print("2. SSH Tunnel: Create an SSH tunnel to the database server")
        print("   Example: ssh -L 5432:localhost:5432 user@100.126.66.97")
        print("   Then connect to localhost:5432 instead")
        print("3. Proxy: Use a database proxy server located in an allowed network")
        
        print(f"\n4. Request firewall/network changes to allow your IP:")
        print(f"   Your IP: 100.89.18.15")
        print(f"   Target: 100.126.66.97:5432")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTroubleshooting interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)