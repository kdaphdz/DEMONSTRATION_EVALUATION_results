import json
import csv
from pathlib import Path

ROOT = Path(__file__).parent
MAIN_DIR = ROOT / "main"
BASELINE_DIR = ROOT / "baseline"
OUTPUT_FILE = ROOT / "energy_results.csv"
JSON_FILE = "decompressed.json"

EVENTS = {
    "power/energy-pkg/": "pkg",
    "power/energy-cores/": "cores",
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_measurements(directory):
    measurements = {}

    if not directory.exists():
        print(f"Directory not found: {directory}")
        return measurements

    for folder in directory.glob("measurement*"):
        if not folder.is_dir():
            continue

        suffix = folder.name.removeprefix("measurement")

        if suffix.isdigit():
            measurements[int(suffix)] = folder

    return measurements


def rounded(value):
    return round(value, 2) if value is not None else None


def main():
    main_measurements = get_measurements(MAIN_DIR)
    baseline_measurements = get_measurements(BASELINE_DIR)

    rows = []

    for measurement_id, main_folder in sorted(main_measurements.items()):
        main_json_path = main_folder / JSON_FILE

        if not main_json_path.exists():
            print(f"Missing main JSON: {main_json_path}")
            continue

        main_data = load_json(main_json_path)
        duration = main_data.get("delta_t_seconds")

        if duration is None:
            print(f"Missing delta_t_seconds: {main_json_path}")
            continue

        baseline_data = None
        baseline_folder = baseline_measurements.get(measurement_id)

        if baseline_folder:
            baseline_json_path = baseline_folder / JSON_FILE

            if baseline_json_path.exists():
                baseline_data = load_json(baseline_json_path)
            else:
                print(f"Missing baseline JSON: {baseline_json_path}")
        else:
            print(f"No baseline for measurement{measurement_id}")

        row = {
            "measurement": f"measurement{measurement_id}",
            "main_time_seconds": rounded(duration),
        }

        for event, prefix in EVENTS.items():
            main_event = main_data.get("events", {}).get(event, {})
            main_consumption = main_event.get("consumption")

            baseline_mean = None
            corrected_consumption = None

            if baseline_data is not None:
                baseline_event = baseline_data.get("events", {}).get(
                    event, {}
                )
                baseline_mean = baseline_event.get("mean")

                if baseline_mean is not None and main_consumption is not None:
                    corrected_consumption = (
                        main_consumption - baseline_mean * duration
                    )

            row[f"{prefix}_main_consumption_J"] = rounded(
                main_consumption
            )
            row[f"{prefix}_baseline_mean_W"] = rounded(
                baseline_mean
            )
            row[f"{prefix}_consumption_without_baseline_J"] = rounded(
                corrected_consumption
            )

        rows.append(row)

    fieldnames = [
        "measurement",
        "main_time_seconds",
        "pkg_main_consumption_J",
        "pkg_baseline_mean_W",
        "pkg_consumption_without_baseline_J",
        "cores_main_consumption_J",
        "cores_baseline_mean_W",
        "cores_consumption_without_baseline_J",
    ]

    with OUTPUT_FILE.open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV generated: {OUTPUT_FILE}")
    print(f"Measurements processed: {len(main_measurements)}")
    print(f"Rows generated: {len(rows)}")


if __name__ == "__main__":
    main()