import sqlite3
import argparse
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "nincore.db")

def main():
    parser = argparse.ArgumentParser(description="NINCore CLI - Fetch Citizen Records")
    parser.add_argument("--limit", type=int, default=5, help="Number of random NINs to fetch (default: 5)")
    parser.add_argument("--nin", type=str, help="Fetch a specific NIN record")
    
    args = parser.parse_args()
    
    if not os.path.exists(DB_PATH):
        print("\n[ERROR] Database not found! Please run setup.bat first.\n")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if args.nin:
        cursor.execute("SELECT NIN, Full_Name, DOB, Gender, State_of_Origin FROM Citizen_Registry WHERE NIN = ?", (args.nin,))
        row = cursor.fetchone()
        if row:
            print("\n" + "="*50)
            print("  CITIZEN RECORD FOUND")
            print("="*50)
            print(f"  NIN:      {row[0]}")
            print(f"  Name:     {row[1]}")
            print(f"  DOB:      {row[2]}")
            print(f"  Gender:   {row[3]}")
            print(f"  State:    {row[4]}")
            print("="*50 + "\n")
        else:
            print(f"\n[ERROR] NIN '{args.nin}' not found in the registry.\n")
    else:
        cursor.execute("SELECT NIN, Full_Name, State_of_Origin FROM Citizen_Registry ORDER BY RANDOM() LIMIT ?", (args.limit,))
        rows = cursor.fetchall()
        print("\n" + "="*65)
        print(f"  FETCHING {args.limit} RANDOM CITIZEN RECORDS")
        print("="*65)
        for i, r in enumerate(rows, 1):
            print(f"  {i}. NIN: {r[0]:<15} | Name: {r[1]:<20} | State: {r[2]}")
        print("="*65 + "\n")
        print("Tip: To fetch a specific NIN, use: python scripts/fetch_nin.py --nin 12345678901\n")
        
    conn.close()

if __name__ == "__main__":
    main()
