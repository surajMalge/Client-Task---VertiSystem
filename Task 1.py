import os
import random
import json
import glob
import time
from collections import defaultdict
from statistics import mean, median

def generate_flights_data(N, output_dir):
    cities = [f"City{i}" for i in range(1, random.randint(100, 200))]
    for month in range(1, 13):
        for city in cities:
            file_name = f"{output_dir}/{month:02d}-YY-{city}-flights.json"
            flights = []
            for _ in range(N):
                flight = {
                    "date": f"{random.randint(1, 28)}/{month:02d}/YY",
                    "origin_city": city,
                    "destination_city": random.choice(cities),
                    "flight_duration_secs": random.randint(3600, 7200),
                    "passengers_on_board": random.randint(0, 200) if random.random() > 0.001 else None
                }
                flights.append(flight)
            with open(file_name, 'w') as f:
                json.dump(flights, f)

def process_files(input_dir):
    total_records = 0
    dirty_records = 0
    start_time = time.time()
    flight_durations = defaultdict(list)
    passengers_arrived = defaultdict(int)
    passengers_left = defaultdict(int)

    for file_path in glob.glob(os.path.join(input_dir, '*.json')):
        with open(file_path) as f:
            flights = json.load(f)
            total_records += len(flights)
            for flight in flights:
                if any(value is None for value in flight.values()):
                    dirty_records += 1
                else:
                    flight_durations[flight['destination_city']].append(flight['flight_duration_secs'])
                    passengers_arrived[flight['destination_city']] += flight['passengers_on_board']
                    passengers_left[flight['origin_city']] += flight['passengers_on_board']

    end_time = time.time()
    run_duration = end_time - start_time

    return total_records, dirty_records, run_duration, flight_durations, passengers_arrived, passengers_left

def analyze_data(flight_durations, passengers_arrived, passengers_left):
    top_25_destinations = sorted(flight_durations.items(), key=lambda x: len(x[1]), reverse=True)[:25]
    avg_flight_durations = {city: mean(durations) for city, durations in top_25_destinations}
    p95_flight_durations = {city: median(sorted(durations)) for city, durations in top_25_destinations}

    max_passengers_arrived = max(passengers_arrived.items(), key=lambda x: x[1])
    max_passengers_left = max(passengers_left.items(), key=lambda x: x[1])

    return avg_flight_durations, p95_flight_durations, max_passengers_arrived, max_passengers_left

if __name__ == "__main__":
    N = 5000
    output_dir = "/tmp/flights"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate_flights_data(N, output_dir)
    total_records, dirty_records, run_duration, flight_durations, passengers_arrived, passengers_left = process_files(output_dir)
    avg_flight_durations, p95_flight_durations, max_passengers_arrived, max_passengers_left = analyze_data(flight_durations, passengers_arrived, passengers_left)

    print(f"Total records processed: {total_records}")
    print(f"Dirty records: {dirty_records}")
    print(f"Total run duration: {run_duration} seconds")

    print("\nAverage flight durations (Top 25 destinations):")
    for city, avg_duration in avg_flight_durations.items():
        print(f"{city}: {avg_duration} seconds")

    print("\nP95 flight durations (Top 25 destinations):")
    for city, p95_duration in p95_flight_durations.items():
        print(f"{city}: {p95_duration} seconds")

    print(f"\nCity with maximum passengers arrived: {max_passengers_arrived[0]}, Passengers: {max_passengers_arrived[1]}")
    print(f"City with maximum passengers left: {max_passengers_left[0]}, Passengers: {max_passengers_left[1]}")

