from collections import defaultdict
import xml.etree.ElementTree as ET
import json
import time
import argparse
from ulid import ULID


def gen_ulid():
    return str(ULID.from_timestamp(time.time()))


def parse_decimal(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def parse_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def parse_bool(val):
    return val.strip().upper() == "Y"


def extract_volume_data(row):
    cells = row.findall(".//{urn:schemas-microsoft-com:office:spreadsheet}Cell")
    data = [
        cell.findtext(".//{urn:schemas-microsoft-com:office:spreadsheet}Data") or ""
        for cell in cells
    ]

    if not any(data):  # skip completely empty rows
        return None

    if len(data) < 22:  # skip rows with insufficient data
        return None
    
    if data[0] == "AIRPORTID":  # skip header row
        return None

    return {
        "id": gen_ulid(),
        "airportId": data[0],
        "volumeId": data[1],
        "name": data[2],
        "runwayThreshold": {
            "lat": parse_decimal(data[20]),
            "lon": parse_decimal(data[21]),
        },
        "ceiling": parse_int(data[8]),
        "floor": parse_int(data[9]),
        "magneticHeading": parse_int(data[10]),
        "maximumHeadingDeviation": parse_int(data[13]),
        "length": parse_decimal(data[7]),
        "widthLeft": parse_int(data[11]),
        "widthRight": parse_int(data[12]),
        "twoPointFiveApproachDistance": parse_decimal(data[14]),
        "twoPointFiveApproachEnabled": parse_bool(data[15]),
        "scratchpads": [],
        "tcps": [],
    }


def extract_scratchpads(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespace = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

    scratchpad_map = defaultdict(list)

    for row in root.findall(".//ss:Row", namespace):
        cells = row.findall(".//ss:Cell", namespace)
        data = [
            cell.findtext(".//ss:Data", default="", namespaces=namespace)
            for cell in cells
        ]

        if not data or data[0] == "AIRPORTID":
            continue
        if len(data) < 5:
            continue

        scratchpad_entry = {
            "id": gen_ulid(),
            "entry": data[2],
            "scratchPadNumber": "One" if data[3].strip() == "1" else "Two",
            "type": (
                "Exclude"
                if data[4].strip().lower().startswith("exclu")
                else "Ineligible"
            ),
        }

        key = (data[0], data[1])  # (airportId, volumeId)
        scratchpad_map[key].append(scratchpad_entry)

    return scratchpad_map


def extract_tcps(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespace = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

    tcp_map = defaultdict(list)

    for row in root.findall(".//ss:Row", namespace):
        cells = row.findall(".//ss:Cell", namespace)
        data = [
            cell.findtext(".//ss:Data", default="", namespaces=namespace)
            for cell in cells
        ]

        if not data or data[0] == "AIRPORTID":
            continue
        if len(data) < 4:
            continue

        tcp_entry = {
            "id": gen_ulid(),
            "tcp": data[2],
            "coneType": "Alert" if data[3] == "Alert" else "AlertAndMonitor",
        }

        key = (data[0], data[1])  # (airportId, volumeId)
        tcp_map[key].append(tcp_entry)

    return tcp_map


def parse_volume_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    namespace = {"ss": "urn:schemas-microsoft-com:office:spreadsheet"}

    rows = root.findall(
        './/ss:Worksheet[@ss:Name="ATPA_VOLUMES"]/ss:Table/ss:Row', namespace
    )
    volumes = [v for row in rows if (v := extract_volume_data(row)) is not None]
    return volumes


def combine(volumes, scratchpad_map, tcp_map):
    for vol in volumes:
        key = (vol["airportId"], vol["volumeId"])
        if key in scratchpad_map:
            vol["scratchpads"] = scratchpad_map[key]
        if key in tcp_map:
            vol["tcps"] = tcp_map[key]
    return volumes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert XML ATPA volumes to JSON format"
    )
    parser.add_argument("input_volumes_file", help="Input VOLUMES XML file path")
    parser.add_argument(
        "input_scratchpads_file", help="Input SCRATCHPADS XML file path"
    )
    parser.add_argument("input_tcps_file", help="Input TCPS XML file path")
    parser.add_argument("output_file", help="Output JSON file path")

    args = parser.parse_args()

    volumes_data = parse_volume_xml(args.input_volumes_file)
    scratchpad_map = extract_scratchpads(args.input_scratchpads_file)
    tcp_map = extract_tcps(args.input_tcps_file)
    combined = combine(volumes_data, scratchpad_map, tcp_map)

    with open(args.output_file, "w") as f:
        json.dump(combined, f, indent=2)

    print(f"Converted {len(combined)} volumes to {args.output_file}")
