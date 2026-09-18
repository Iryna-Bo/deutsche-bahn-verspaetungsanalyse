import os
import urllib.request
import xml.etree.ElementTree as ET

from dotenv import load_dotenv


load_dotenv()

CLIENT_ID = os.getenv("DB_CLIENT_ID")
CLIENT_SECRET = os.getenv("DB_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError(
        "DB_CLIENT_ID or DB_CLIENT_SECRET is not set."
    )


base_url = (
    "https://apis.deutschebahn.com/"
    "db-api-marketplace/apis/timetables/v1"
)

plan_url = f"{base_url}/plan/8000105/260917/20"
fchg_url = f"{base_url}/fchg/8000105"


def get_xml(url):
    request = urllib.request.Request(
        url,
        headers={
            "DB-Client-Id": CLIENT_ID,
            "DB-Api-Key": CLIENT_SECRET,
        },
    )

    with urllib.request.urlopen(request) as response:
        return response.read()


plan_root = ET.fromstring(get_xml(plan_url))
fchg_root = ET.fromstring(get_xml(fchg_url))


plan_ids = {
    stop.attrib.get("id")
    for stop in plan_root.findall("s")
}

fchg_ids = {
    stop.attrib.get("id")
    for stop in fchg_root.findall("s")
}


matches = plan_ids & fchg_ids


print(f"PLAN stops: {len(plan_ids)}")
print(f"FCHG stops: {len(fchg_ids)}")
print(f"Matching stop IDs: {len(matches)}")
print()


for stop_id in list(matches)[:10]:
    print(stop_id)