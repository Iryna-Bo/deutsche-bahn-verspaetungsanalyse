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


url = (
    "https://apis.deutschebahn.com/"
    "db-api-marketplace/apis/timetables/v1/"
    "fchg/8000105"
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

count = 0

for stop in root.findall("s"):
    train = stop.find("tl")

    for event_type in ["ar", "dp"]:
        event = stop.find(event_type)

        if event is None:
            continue

        planned = event.attrib.get("pt")
        changed = event.attrib.get("ct")

        if planned and changed:
            planned_time = parse_db_time(planned)
            changed_time = parse_db_time(changed)

            delay_minutes = (
                changed_time - planned_time
            ).total_seconds() / 60

            train_number = (
                train.attrib.get("n")
                if train is not None
                else None
            )

            train_type = (
                train.attrib.get("c")
                if train is not None
                else None
            )

            line = event.attrib.get("l")

            print(
                f"{event_type.upper()} | "
                f"Train: {train_number} | "
                f"Type: {train_type} | "
                f"Line: {line} | "
                f"Planned: {planned_time} | "
                f"Changed: {changed_time} | "
                f"Delay: {delay_minutes:.0f} min"
            )

            count += 1

            if count >= 10:
                raise SystemExit