import pandas as pd
from datetime import datetime

def update_expiry_status(csv_file_path):
    df = pd.read_csv(csv_file_path)

    # Convert to datetime
    df['Last Date to Apply'] = pd.to_datetime(df['Last Date to Apply'], errors='coerce')

    def check_expiry(date_val):
        if pd.isna(date_val):
            return "Unknown"
        
        today_date = pd.Timestamp.today().normalize()
        last_date = pd.to_datetime(date_val).normalize()

        # Debug line (optional)
        #print(f"Comparing Last Date: {last_date.date()} with Today: {today_date.date()}")

        if last_date < today_date:
            return "Expired"
        else:
            return "Currently Open"

    df['Expiry'] = df['Last Date to Apply'].apply(check_expiry)

    df.to_csv(csv_file_path, index=False)
    print("Expiry status updated successfully.")
