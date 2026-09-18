import os
import urllib.request
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("DB_CLIENT_ID")
CLIENT_SECRET = os.getenv("DB_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        "DB_CLIENT_ID or DB_CLIENT_SECRET is not set."
    )

url = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/8000105/260917/11"

request = urllib.request.Request(
    url,
    headers={
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": CLIENT_SECRET,
    },
)

with urllib.request.urlopen(request) as response:
    xml = response.read().decode("utf-8")

print(xml[:3000])