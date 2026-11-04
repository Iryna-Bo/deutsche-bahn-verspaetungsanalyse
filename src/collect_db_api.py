
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

BERLIN_TZ = ZoneInfo("Europe/Berlin")

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

BASE_DIR = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
    / "api_current"
)


# --------------------------------------------------
# API request
# --------------------------------------------------

def get_xml(url):
    request = urllib.request.Request(
        url,
        headers={
            "DB-Client-Id": CLIENT_ID,
            "DB-Api-Key": CLIENT_SECRET,
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


# --------------------------------------------------
# Time conversion
# --------------------------------------------------

def parse_db_time(value):
    if value is None:
        return None

    try:
        return datetime.strptime(
            value,
            "%y%m%d%H%M",
        ).replace(tzinfo=BERLIN_TZ)

    except ValueError:
        return None


# --------------------------------------------------
# Collect one station
# --------------------------------------------------

def collect_station_snapshot(
    station_name,
    station_eva,
    snapshot_time,
):
    date = snapshot_time.strftime("%y%m%d")
    hour = snapshot_time.strftime("%H")

    plan_url = (
        f"{BASE_URL}/plan/"
        f"{station_eva}/{date}/{hour}"
    )

    fchg_url = (
        f"{BASE_URL}/fchg/{station_eva}"
    )

    print(f"Collecting {station_name}...")

    plan_xml = get_xml(plan_url)
    fchg_xml = get_xml(fchg_url)

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

            records.append({
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
                "collected_at": snapshot_time,
            })

    df = pd.DataFrame(records)

    print(f"  Records collected: {len(df)}")

    return df


# --------------------------------------------------
# Collect all stations
# --------------------------------------------------

def collect_all_stations(snapshot_time):

    snapshots = []

    for station_name, station_eva in STATIONS.items():

        df = collect_station_snapshot(
            station_name=station_name,
            station_eva=station_eva,
            snapshot_time=snapshot_time,
        )

        df["snapshot_id"] = (
            snapshot_time.strftime("%Y-%m-%d_%H-%M")
        )

        snapshots.append(df)

    if not snapshots:
        return pd.DataFrame()

    return pd.concat(
        snapshots,
        ignore_index=True,
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":

    snapshot_time = datetime.now(BERLIN_TZ)

    print("Starting DB API snapshot collection...")
    print(f"Snapshot time: {snapshot_time}")
    print(f"Stations: {len(STATIONS)}")
    print()

    df = collect_all_stations(
        snapshot_time=snapshot_time,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not df.empty:

        output_path = (
            OUTPUT_DIR
            / (
                "snapshot_"
                + snapshot_time.strftime(
                    "%Y-%m-%d_%H-%M"
                )
                + ".parquet"
            )
        )

        table = pa.Table.from_pandas(
            df,
            preserve_index=False,
        )

        pq.write_table(
            table,
            output_path,
        )

        print()
        print(f"Snapshot records: {len(df)}")
        print(f"Saved to: {output_path}")

    else:
        print("No records collected.")

    print()
    print("Snapshot collection finished.")
