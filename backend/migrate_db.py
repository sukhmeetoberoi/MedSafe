import sqlite3
import os

db_path = "./medsummarize.db"

if not os.path.exists(db_path):
    print(f"Database file not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of columns to check and add
        new_columns = [
            ("phi_redacted_text", "TEXT"),
            ("phi_redacted_pages", "TEXT"),
            ("phi_report", "TEXT")
        ]
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(reports)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        for col_name, col_type in new_columns:
            if col_name not in existing_columns:
                print(f"Adding column '{col_name}'...")
                cursor.execute(f"ALTER TABLE reports ADD COLUMN {col_name} {col_type}")
            else:
                print(f"Column '{col_name}' already exists.")
        
        conn.commit()
        conn.close()
        print("Migration check complete.")
    except sqlite3.OperationalError as e:
        print(f"Operational error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
