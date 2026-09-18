
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("DB_CLIENT_ID")
CLIENT_SECRET = os.getenv("DB_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        "DB_CLIENT_ID or DB_CLIENT_SECRET is not set."
    )


def parse_db_time(value):
    if value is None:
        return None

    return datetime.strptime(value, "%y%m%d%H%M")


station_eva = "8000105"

url = (
    "https://apis.deutschebahn.com/"
    "db-api-marketplace/apis/timetables/v1/"
    "plan/8000105/260917/11"
)

request = urllib.request.Request(
    url,
    headers={
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": CLIENT_SECRET,
    },
)


with urllib.request.urlopen(request) as response:
    xml = response.read()


root = ET.fromstring(xml)

station_name = root.attrib.get("station")

records = []


for stop in root.findall("s"):
    train = stop.find("tl")

    if train is None:
        continue

    stop_id = stop.attrib.get("id")

    train_number = train.attrib.get("n")
    train_type = train.attrib.get("c")
    line = train.attrib.get("l")

    arrival = stop.find("ar")
    departure = stop.find("dp")

    arrival_time = None
    departure_time = None

    if arrival is not None:
        arrival_time = parse_db_time(
            arrival.attrib.get("pt")
        )

    if departure is not None:
        departure_time = parse_db_time(
            departure.attrib.get("pt")
        )

    record = {
        "station_eva": station_eva,
        "station_name": station_name,
        "stop_id": stop_id,
        "train_number": train_number,
        "train_type": train_type,
        "line": line,
        "planned_arrival": arrival_time,
        "planned_departure": departure_time,
    }

    records.append(record)


print(f"Station: {station_name}")
print(f"EVA: {station_eva}")
print(f"Number of records: {len(records)}")
print()

for record in records[:5]:
    print(record)