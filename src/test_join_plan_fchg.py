import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("DB_CLIENT_ID")
CLIENT_SECRET = os.getenv("DB_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        "DB_CLIENT_ID or DB_CLIENT_SECRET is not set."
    )


BASE_URL = (
    "https://apis.deutschebahn.com/"
    "db-api-marketplace/apis/timetables/v1"
)

STATION_EVA = "8000105"
DATE = "260917"
HOUR = "20"


def get_xml(url):
    collected_at = datetime.now()

    request = urllib.request.Request(
        url,
        headers={
            "DB-Client-Id": CLIENT_ID,
            "DB-Api-Key": CLIENT_SECRET,
        },
    )

    with urllib.request.urlopen(request) as response:
        xml = response.read()

    return xml, collected_at


def parse_db_time(value):
    if value is None:
        return None

    return datetime.strptime(value, "%y%m%d%H%M")


plan_url = (
    f"{BASE_URL}/plan/"
    f"{STATION_EVA}/{DATE}/{HOUR}"
)

fchg_url = (
    f"{BASE_URL}/fchg/"
    f"{STATION_EVA}"
)


plan_xml, plan_collected_at = get_xml(plan_url)
fchg_xml, fchg_collected_at = get_xml(fchg_url)

plan_root = ET.fromstring(plan_xml)
fchg_root = ET.fromstring(fchg_xml)


# Find the first plan stop that also exists in fchg
fchg_stops = {
    stop.attrib.get("id"): stop
    for stop in fchg_root.findall("s")
}


# Find matching stops in fchg
fchg_stops = {
    stop.attrib.get("id"): stop
    for stop in fchg_root.findall("s")
}


records = []


for plan_stop in plan_root.findall("s"):

    stop_id = plan_stop.attrib.get("id")

    if stop_id not in fchg_stops:
        continue

    fchg_stop = fchg_stops[stop_id]

    train = plan_stop.find("tl")

    train_number = None
    train_type = None

    if train is not None:
        train_number = train.attrib.get("n")
        train_type = train.attrib.get("c")

    for event_type in ["ar", "dp"]:

        plan_event = plan_stop.find(event_type)
        fchg_event = fchg_stop.find(event_type)

        if plan_event is None:
            continue

        planned = plan_event.attrib.get("pt")

        changed = None

        if fchg_event is not None:
            changed = fchg_event.attrib.get("ct")

        planned_time = parse_db_time(planned)
        changed_time = parse_db_time(changed)

        delay_minutes = None

        if planned_time and changed_time:
            delay_minutes = (
                changed_time - planned_time
            ).total_seconds() / 60

        record = {
    "stop_id": stop_id,
    "train_number": train_number,
    "train_type": train_type,
    "event_type": event_type,
    "planned_time": planned_time,
    "changed_time": changed_time,
    "delay_minutes": delay_minutes,
    "collected_at": fchg_collected_at,
}

        records.append(record)


print(f"Number of records: {len(records)}")
print()

for record in records[:10]:
    print(record)

df = pd.DataFrame(records)

print()
print(df.head(10))
print()
print(df.dtypes)

df.to_parquet(
    "data/processed/test_db_snapshot.parquet",
    index=False
)

print()
print("Parquet file saved successfully.")