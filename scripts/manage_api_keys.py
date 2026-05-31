"""
NINCore API Key Management CLI
==============================
Interactive script to generate, revoke, and manage API keys for sector agencies.
Designed for administrative use and presentation demonstrations.
"""

import sqlite3
import secrets
import bcrypt
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "nincore.db")

def print_header():
    print("\n" + "="*55)
    print("   NINCore Secure API Key Management Terminal")
    print("="*55)

def connect_db():
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: Database not found at {DB_PATH}")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def generate_key_and_hash():
    secret = secrets.token_hex(32)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(secret.encode('utf-8'), salt).decode('utf-8')
    return secret, hashed

def main():
    print_header()
    conn = connect_db()
    cursor = conn.cursor()

    # List current agencies
    cursor.execute("SELECT Agency_ID, Sector_Name, Status FROM API_Keys")
    agencies = cursor.fetchall()
    
    print("\nCurrent Agencies in System:")
    print(f"  {'Agency ID':<20} | {'Sector':<15} | {'Status':<8}")
    print("  " + "-"*50)
    for row in agencies:
        print(f"  {row[0]:<20} | {row[1]:<15} | {row[2]:<8}")

    print("\nOptions:")
    print("  1. Rotate/Regenerate key for an existing Agency")
    print("  2. Provision key for a NEW Agency")
    print("  3. Exit")
    
    choice = input("\nSelect an option (1-3): ").strip()
    
    if choice == '1':
        agency_id = input("Enter the Agency ID to regenerate: ").strip()
        
        cursor.execute("SELECT Sector_Name FROM API_Keys WHERE Agency_ID = ?", (agency_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"\n[!] Error: Agency '{agency_id}' not found.")
            return
            
        print(f"\n[*] Revoking old key for {agency_id}...")
        print(f"[*] Generating new cryptographic key...")
        secret, hashed = generate_key_and_hash()
        full_key = f"{agency_id}:{secret}"
        
        cursor.execute("UPDATE API_Keys SET API_Key = ?, Status = 'Active' WHERE Agency_ID = ?", (hashed, agency_id))
        conn.commit()
        
        print("\n" + "*"*65)
        print("  KEY ROTATION SUCCESSFUL - OLD KEY IS NOW INVALID")
        print("*"*65)
        print(f"  API Key: {full_key}")
        print("*"*65)
        print("  IMPORTANT: Copy this key immediately. It cannot be recovered.\n")
        
    elif choice == '2':
        agency_id = input("Enter new Agency ID (e.g., TAX_FIRS_001): ").strip()
        sector_name = input("Enter Sector Name (e.g., Taxation): ").strip()
        
        cursor.execute("SELECT 1 FROM API_Keys WHERE Agency_ID = ?", (agency_id,))
        if cursor.fetchone():
            print(f"\n[!] Error: Agency '{agency_id}' already exists. Use option 1 to rotate.")
            return
            
        print(f"\n[*] Provisioning new agency and generating key...")
        secret, hashed = generate_key_and_hash()
        full_key = f"{agency_id}:{secret}"
        
        cursor.execute("INSERT INTO API_Keys (Agency_ID, Sector_Name, API_Key, Status) VALUES (?, ?, ?, 'Active')", 
                       (agency_id, sector_name, hashed))
        conn.commit()
        
        print("\n" + "*"*65)
        print("  NEW AGENCY PROVISIONED SUCCESSFULLY")
        print("*"*65)
        print(f"  Agency ID: {agency_id}")
        print(f"  API Key  : {full_key}")
        print("*"*65)
        print("  IMPORTANT: Provide this key to the agency securely.\n")
        
    elif choice == '3':
        print("Exiting...")
    else:
        print("Invalid choice.")
        
    conn.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
