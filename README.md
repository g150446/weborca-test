# Web ORCA Database Testing Scripts

This repository contains Python scripts for testing and interacting with a Web ORCA PostgreSQL database. Web ORCA is a Japanese medical record system, and these scripts provide various utilities for database connectivity testing, schema exploration, and patient data analysis.

## Prerequisites

- Python 3.x
- `pyodbc` module (`pip install pyodbc`)
- PostgreSQL ODBC drivers installed on your system
- Access to a Web ORCA PostgreSQL database

## Scripts Overview

### 1. `test_orca_odbc.py`
**Primary Script - Comprehensive ODBC Connection Testing and Patient Management**

This is the main utility script that provides multiple functions for Web ORCA database interaction:

**Features:**
- Tests ODBC connectivity using both ANSI and Unicode PostgreSQL drivers
- Lists all patients with detailed information (ID, name, gender, birth date)
- Searches patients by name or phonetic name (kananame)
- Shows today's hospital visits with department statistics
- Interactive connection testing with custom parameters
- Comprehensive error handling and Japanese language support

**Usage:**
```bash
python3 test_orca_odbc.py                # Basic connection test + patient summary
python3 test_orca_odbc.py --patients     # List all registered patients
python3 test_orca_odbc.py --search       # Interactive patient search
python3 test_orca_odbc.py --today        # Show today's hospital visits
python3 test_orca_odbc.py --interactive  # Custom connection test
python3 test_orca_odbc.py --help         # Show usage help
```

### 2. `check_today_visits.py`
**Today's Visit Checker**

A focused script that specifically checks for patient visits on the current date.

**Features:**
- Retrieves and displays today's patient visits from `tbl_uketuke` table
- Shows visit times, patient IDs, names, and departments
- Also displays recent visits from the last 7 days for testing purposes
- Joins patient reception data (`tbl_uketuke`) with patient information (`tbl_ptinf`)

**Key Tables Used:**
- `tbl_uketuke`: Reception/visit records
- `tbl_ptinf`: Patient information

### 3. `examine_patient_tables.py`
**Patient Table Structure Analyzer**

Examines the structure and sample data of the main patient information table.

**Features:**
- Displays the complete schema structure of `tbl_ptinf` table
- Shows column names and their data types
- Provides sample records (first 3 entries) to understand data format
- Useful for database schema exploration and development

### 4. `examine_schema.py`
**Database Schema Explorer**

A comprehensive database schema exploration tool.

**Features:**
- Lists all tables in the public schema
- Identifies potential patient-related tables by name patterns
- Examines table structures (columns and data types) for patient tables
- Searches for tables containing keywords like 'patient', 'ptnt', 'kanja', '患者'

### 5. `examine_visits.py`
**Visit/Appointment Table Explorer**

Focuses on analyzing visit and appointment-related database structures.

**Features:**
- Searches for visit/appointment related tables using pattern matching
- Examines structures of visit tables like `tbl_uketuke` and `tbl_jyurrk`
- Shows sample visit data to understand record formats
- Tests date formatting functions used in the database
- Helps understand the relationship between different visit-tracking tables

**Key Tables Analyzed:**
- `tbl_uketuke`: Reception/appointment table
- `tbl_jyurrk`: Visit records table
- Other visit-related tables with patterns like 'sryact', 'nyukin'

## Database Connection Details

All scripts use the following default connection parameters:
- **Server:** 100.126.66.97
- **Port:** 5432
- **Database:** orca
- **Username:** orca
- **Password:** orca
- **Driver:** PostgreSQL Unicode (with ANSI fallback)

## Common Database Tables

Based on the scripts, the main Web ORCA tables include:

- **`tbl_ptinf`**: Patient information (names, demographics, contact info)
- **`tbl_uketuke`**: Reception/visit records (appointment times, departments)
- **`tbl_jyurrk`**: Visit history records

## Security Notes

⚠️ **Important**: These scripts contain hardcoded database credentials for testing purposes. In a production environment:
- Use environment variables or secure credential management
- Implement proper authentication and authorization
- Follow your organization's security policies
- Change default passwords

## Error Handling

All scripts include comprehensive error handling for:
- Database connection failures
- Missing ODBC drivers
- Authentication errors
- Query execution problems
- Data formatting issues

## Japanese Language Support

The scripts include Japanese language support for:
- Patient names and phonetic names (kananame)
- Department names (診療科)
- Status messages and output formatting
- Date formatting in Japanese style (年月日)