import schedule
import time
from datetime import datetime, timedelta
import requests
import json
import os
from supabase import create_client, Client

webhook_url = os.environ['WEBHOOK_URL']
colors = {
    "happy": "#ecba3d",
    "sad": "#224a81",
    "angry": "#932323",
    "content": "#c4c936",
    "lonely": "#344864",
    "anxious": "#b0431f",
    "proud": "#e2d112",
    "disappointed": "#37548a",
    "frusturated": "#610303",
    "excited": "#e38a04",
    "tired": "#788aa4",
    "stressed": "#c24244",
    "optimistic": "#9bbc23",
    "depressed": "#0a1627",
    "confused": "#a0547b",
}

SUPABASE_URL = "https://qzeihdpxiklgqyflggjv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF6ZWloZHB4aWtsZ3F5ZmxnZ2p2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4Nzk1NTAsImV4cCI6MjA1OTQ1NTU1MH0.jtiUrPywII-ucmMtWuP8INhfkCs1wS8DVmOnODY7Xmg"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def job():
    print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}: Grabbing data")
    entries = get_yesterday_entries()
    counts = count_each_emotion(entries)
    sorted_counts = {k: v for k, v in sorted(counts.items(), key = lambda item: item[1], reverse=True)}
    frequent_color = list(sorted_counts.keys())[0].lower()
    frequent_color_hex = colors.get(frequent_color, "#ffffff")
    body = format_content(sorted_counts)
    print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}: Sending data to Discord")
    send_to_discord(body, frequent_color_hex[1:])

def get_yesterday_entries():
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_date = datetime.strftime(yesterday, "%Y-%m-%d")

    response = (
        supabase.table("entries")
        .select('*')
        .gte('created_at', yesterday_date + 'T00:00:00Z')
        .lt('created_at', yesterday_date + 'T23:59:59Z')
        .order('created_at', desc=False)
        .execute()
    )

    return response.data

def count_each_emotion(entries):
    emotion_counts = {}

    for i in range(len(entries)):
        entry = entries[i]["entry"]
        if entry in emotion_counts.keys():
            emotion_counts[entry] += 1
        else:
            emotion_counts[entry] = 1

    return emotion_counts

def format_content(entries):
    content = ""
    for key, value in entries.items():
        content += f"{key}: {value}\n"

    return content

def send_to_discord(body, top_color):
    data = {
        "content": "**This is howWEfelt yesterday**\n" + body + "Be sure to submit howYOUfeel today! [howWEfeel](https://mehrezat.com/howWEfeel/home.html)",
        "username": "howWEfeel",
        "avatar_url": f"https://dummyimage.com/80x80/{top_color}/{top_color}.png"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 204:
        print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}: Message sent successfully")
    else:
        print(f"{datetime.today().strftime('%Y-%m-%d %H:%M:%S')}: Failed to send message: {response.status_code} - {response.text}")

job()
schedule.every().saturday.at("08:00").do(job)
schedule.every().sunday.at("08:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
