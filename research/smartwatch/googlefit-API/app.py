import datetime
import json
import os
import pickle
import pandas as pd
import numpy as np
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Google Fit API Configuration
SCOPES = [
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'
]

# Google Fit Credentials
def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

# Get heart rate data from the past 12 hours
def get_heart_rate_data(service):
    data_source = "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm"
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=12)  # Last 12 hours
    
    body = {
        "aggregateBy": [{"dataTypeName": "com.google.heart_rate.bpm", "dataSourceId": data_source}],
        "bucketByTime": {"durationMillis": 900000},  # 15-minute intervals
        "startTimeMillis": int(start_time.timestamp() * 1000),
        "endTimeMillis": int(end_time.timestamp() * 1000)
    }
    
    response = service.users().dataset().aggregate(userId="me", body=body).execute()
    heart_rate_data = []

    for bucket in response.get('bucket', []):
        timestamp = datetime.datetime.fromtimestamp(int(bucket.get('startTimeMillis')) / 1000)
        for dataset in bucket.get('dataset', []):
            for point in dataset.get('point', []):
                if point.get('value'):
                    heart_rate_data.append({'timestamp': timestamp, 'heart_rate_bpm': point['value'][0]['fpVal']})
    
    df = pd.DataFrame(heart_rate_data)
    
    if not df.empty:
        df['heart_rate_bpm_int'] = df['heart_rate_bpm'].astype(int)
        hr_list = df['heart_rate_bpm_int'].tolist()
        min_hr = int(min(hr_list)) if hr_list else 0
        max_hr = int(max(hr_list)) if hr_list else 0
        avg_hr = round(sum(hr_list) / len(hr_list)) if hr_list else 0
        std_hr = round(np.std(hr_list), 1) if hr_list else 0
    else:
        hr_list, avg_hr, min_hr, max_hr, std_hr = [], 0, 0, 0, 0

    return df, hr_list, avg_hr, min_hr, max_hr, std_hr

# Get sleep data from the past day
def get_sleep_data_past_day(service):
    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(days=1)
    request = service.users().sessions().list(
        userId="me",
        startTime=start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        endTime=end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        activityType=72  # 72 is the activity type for sleep
    )
    response = request.execute()
    print("\nSleep API raw response:", json.dumps(response, indent=2))
    
    sleep_data = []
    for session in response.get('session', []):
        start_millis = int(session['startTimeMillis'])
        end_millis = int(session['endTimeMillis'])
        duration_minutes = (end_millis - start_millis) / (1000 * 60)
        start_time = datetime.datetime.fromtimestamp(start_millis / 1000)
        end_time = datetime.datetime.fromtimestamp(end_millis / 1000)
        
        sleep_data.append({
            'start_time': start_time,
            'end_time': end_time,
            'duration_minutes': duration_minutes
        })
    
    return sleep_data

def main():
    try:
        print("Fetching Google Fit data...")
        creds = get_credentials()
        service = build('fitness', 'v1', credentials=creds)
        
        # Get and display heart rate data
        hr_df, hr_list, avg_hr, min_hr, max_hr, std_hr = get_heart_rate_data(service)
        
        print("\n===== HEART RATE DATA (Last 12 Hours) =====")
        if not hr_df.empty:
            print(f"Number of heart rate readings: {len(hr_df)}")
            print(f"Average heart rate: {avg_hr} BPM")
            print(f"Minimum heart rate: {min_hr} BPM")
            print(f"Maximum heart rate: {max_hr} BPM")
            print(f"Heart rate standard deviation: {std_hr}")
            
            print("\nHeart Rate Readings (last 10):")
            for _, row in hr_df.tail(10).iterrows():
                print(f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}: {row['heart_rate_bpm_int']} BPM")
        else:
            print("No heart rate data found for the last 12 hours.")
        
        # Get and display sleep data
        sleep_data = get_sleep_data_past_day(service)
        
        print("\n===== SLEEP DATA (Last 24 Hours) =====")
        if sleep_data:
            print(f"Number of sleep sessions: {len(sleep_data)}")
            for i, session in enumerate(sleep_data):
                print(f"\nSleep Session #{i+1}:")
                print(f"  Start time: {session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  End time: {session['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Duration: {round(session['duration_minutes'])} minutes ({round(session['duration_minutes']/60, 1)} hours)")
        else:
            print("No sleep data found for the last 24 hours.")
            
    except Exception as e:
        print(f"Error fetching Google Fit data: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()