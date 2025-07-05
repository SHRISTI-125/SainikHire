import pandas as pd
from datetime import datetime

def update_expiry_status(csv_file_path):
    df = pd.read_csv(csv_file_path)

    # Convert to datetime
    df['Last Date to Apply'] = pd.to_datetime(df['Last Date to Apply'], errors='coerce')
    today = pd.Timestamp.today()

    def check_expiry(date_val):
        if pd.isna(date_val):
            return "Unknown"
        if date_val < today:
            return "Expired"
        else:
            return "Currently Open"

    df['Expiry'] = df['Last Date to Apply'].apply(check_expiry)

    df.to_csv(csv_file_path, index=False)
    print("Expiry status updated successfully.")
