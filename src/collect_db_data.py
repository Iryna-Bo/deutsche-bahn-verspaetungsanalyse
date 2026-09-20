import os
import time
import urllib.request
import pyarrow as pa
import pyarrow.parquet as pq
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


STATIONS = {
    "Frankfurt(Main)Hbf": "8000105",
    "Mannheim Hbf": "8000244",
    "Stuttgart Hbf": "8000096",
    "Köln Hbf": "8000207",
    "Hamburg Hbf": "8002549",
    "Berlin Hbf": "8098160",
}


INTERVAL_MINUTES = 10
TEST_DURATION_MINUTES = 30

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

def collect_station_snapshot(station_name, station_eva):
    now = datetime.now()

    date = now.strftime("%y%m%d")
    hour = now.strftime("%H")

    plan_url = f"{BASE_URL}/plan/{station_eva}/{date}/{hour}"
    fchg_url = f"{BASE_URL}/fchg/{station_eva}"

    print(f"Collecting {station_name}...")
    print(f"  Plan: {date} {hour}:00")

    plan_xml, plan_collected_at = get_xml(plan_url)
    fchg_xml, fchg_collected_at = get_xml(fchg_url)

    plan_root = ET.fromstring(plan_xml)
    fchg_root = ET.fromstring(fchg_xml)

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
        line = None

        if train is not None:
            train_number = train.attrib.get("n")
            train_type = train.attrib.get("c")
            line = train.attrib.get("l")

        arrival = plan_stop.find("ar")
        departure = plan_stop.find("dp")

        if line is None and arrival is not None:
            line = arrival.attrib.get("l")

        if line is None and departure is not None:
            line = departure.attrib.get("l")

        for event_type in ["ar", "dp"]:

            plan_event = plan_stop.find(event_type)
            fchg_event = fchg_stop.find(event_type)

            if plan_event is None:
                continue

            planned_time = parse_db_time(
                plan_event.attrib.get("pt")
            )

            changed_time = None

            if fchg_event is not None:
                changed_time = parse_db_time(
                    fchg_event.attrib.get("ct")
                )

            delay_minutes = None

            if planned_time and changed_time:
                delay_minutes = (
                    changed_time - planned_time
                ).total_seconds() / 60

            record = {
                "station_eva": station_eva,
                "station_name": station_name,
                "stop_id": stop_id,
                "train_number": train_number,
                "train_type": train_type,
                "line": line,
                "event_type": event_type,
                "planned_time": planned_time,
                "changed_time": changed_time,
                "delay_minutes": delay_minutes,
                "collected_at": fchg_collected_at,
            }

            records.append(record)

    df = pd.DataFrame(records)

    print(f"  Records collected: {len(df)}")

    return df

def collect_all_stations(snapshot_id):
    snapshots = []

    for station_name, station_eva in STATIONS.items():
        df = collect_station_snapshot(
            station_name,
            station_eva,
        )

        df["snapshot_id"] = snapshot_id

        snapshots.append(df)

    if not snapshots:
        return pd.DataFrame()

    return pd.concat(
        snapshots,
        ignore_index=True,
    )

if __name__ == "__main__":
    output_dir = "data/processed/api_current"
    os.makedirs(output_dir, exist_ok=True)

    print("Starting DB API snapshot collection...")
    print(f"Output directory: {output_dir}")
    print()

    df = collect_all_stations(snapshot_id=1)

    if not df.empty:
        collected_date = (
            df["collected_at"]
            .dt.strftime("%Y-%m-%d")
            .iloc[0]
        )

        collected_time = (
            df["collected_at"]
            .dt.strftime("%H-%M")
            .iloc[0]
        )

        output_path = (
            f"{output_dir}/"
            f"snapshot_{collected_date}_{collected_time}.parquet"
        )

        table = pa.Table.from_pandas(
            df,
            preserve_index=False,
        )

        pq.write_table(table, output_path)

        print()
        print(f"Snapshot records: {len(df)}")
        print(f"Saved to: {output_path}")
    else:
        print("No records collected.")

    print()
    print("Snapshot collection finished.")