import duckdb
import pandas as pd

URL = "https://huggingface.co/datasets/piebro/deutsche-bahn-data/resolve/main/monthly_processed_data/data-2025-03.parquet"

tests = [
    ("2048", "IC", "2025-03-15"),
    ("920", "ICE", "2025-03-15"),
    ("3670", "RE", "2025-03-03"),
    ("2500", "ICE", "2025-03-15"),
    ("2500", "ICE", "2025-03-16"),
]

con = duckdb.connect()

query = f"""
SELECT
    train_line_ride_id,
    train_line_station_num,
    station_name,
    train_number,
    train_type,
    COALESCE(departure_planned_time, arrival_planned_time) AS planned_event_time,
    final_destination_station,
    delay_in_min,
    arrival_is_canceled,
    departure_is_canceled,
    is_replacement_train
FROM read_parquet('{URL}')
WHERE train_number IN ('2048', '920', '3670', '2500')
  AND COALESCE(departure_planned_time, arrival_planned_time) IS NOT NULL
  AND COALESCE(departure_planned_time, arrival_planned_time) >= '2025-03-02 00:00:00'
  AND COALESCE(departure_planned_time, arrival_planned_time) < '2025-03-18 08:00:00'
ORDER BY train_number, train_type, train_line_ride_id, planned_event_time
"""

df = con.execute(query).df()
df["planned_event_time"] = pd.to_datetime(df["planned_event_time"])


def split_sequences(g):
    g = g.sort_values("planned_event_time").copy()

    positions = g["train_line_station_num"].tolist()

    groups = []
    current = []

    for _, row in g.iterrows():

        if not current:
            current.append(row)
            continue

        previous = current[-1]

        prev_pos = previous["train_line_station_num"]
        curr_pos = row["train_line_station_num"]

        prev_time = previous["planned_event_time"]
        curr_time = row["planned_event_time"]

        same_position = curr_pos == prev_pos
        backwards = curr_pos < prev_pos
        long_gap = curr_time - prev_time > pd.Timedelta(hours=6)

        if backwards or long_gap:
            groups.append(pd.DataFrame(current))
            current = [row]

        elif same_position:
            if (
                previous["is_replacement_train"]
                != row["is_replacement_train"]
                or previous["departure_is_canceled"]
                != row["departure_is_canceled"]
                or previous["arrival_is_canceled"]
                != row["arrival_is_canceled"]
            ):
                groups.append(pd.DataFrame(current))
                current = [row]
            else:
                current.append(row)

        else:
            current.append(row)

    if current:
        groups.append(pd.DataFrame(current))

    return groups


def analyze_train(train_number, train_type, target_date):

    d = pd.Timestamp(target_date)

    start = d - pd.Timedelta(hours=6)
    end = d + pd.Timedelta(days=1, hours=8)

    x = df[
        (df["train_number"] == train_number)
        & (df["train_type"] == train_type)
        & (df["planned_event_time"] >= start)
        & (df["planned_event_time"] < end)
    ].copy()

    if x.empty:
        return []

    results = []

    for ride_id, ride in x.groupby("train_line_ride_id", sort=False):

        ride = ride.sort_values("planned_event_time")

        sequences = split_sequences(ride)

        for seq in sequences:

            if len(seq) < 2:
                continue

            first = seq.iloc[0]
            last = seq.iloc[-1]

            first_date = first["planned_event_time"].date()

            if first_date != d.date():
                continue

            results.append(seq)

    return results


for train_number, train_type, target_date in tests:

    print()
    print("=" * 100)
    print(f"{train_type} {train_number} | {target_date}")
    print("=" * 100)

    results = analyze_train(
        train_number,
        train_type,
        target_date
    )

    print(f"Gefundene mögliche Routen: {len(results)}")

    for i, route in enumerate(results, start=1):

        first = route.iloc[0]
        last = route.iloc[-1]

        positions = route["train_line_station_num"].tolist()

        stations = route["station_name"].tolist()

        print()
        print(
            f"ROUTE {i} | "
            f"Ride ID {first['train_line_ride_id']} | "
            f"{len(route)} Station Events"
        )

        print(
            f"{first['planned_event_time']} "
            f"{first['station_name']} "
            f"-> "
            f"{last['planned_event_time']} "
            f"{last['station_name']}"
        )

        print(f"Station positions: {positions}")

        print("Route:")

        for _, r in route.iterrows():

            flags = []

            if r["arrival_is_canceled"]:
                flags.append("arrival_cancelled")

            if r["departure_is_canceled"]:
                flags.append("departure_cancelled")

            if r["is_replacement_train"]:
                flags.append("replacement")

            flag_text = ""

            if flags:
                flag_text = " [" + ", ".join(flags) + "]"

            print(
                f"{int(r['train_line_station_num']):>3} | "
                f"{r['planned_event_time']} | "
                f"{r['station_name']}{flag_text} | "
                f"delay={r['delay_in_min']}"
            )