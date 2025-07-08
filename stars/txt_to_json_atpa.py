import json
import argparse
import time
from collections import defaultdict
from ulid import ULID
import re


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


def parse_volume_blocks(text):
  # Extract the section between "******* ATPA_VOLUMES *******" and "******* ATPA_TCP_EXCLUSIONS *******"
  match = re.search(
    r"\*{7} ATPA_VOLUMES \*{7}\n(.*?)\n\*{7} ATPA_TCP_EXCLUSIONS \*{7}",
    text,
    re.DOTALL
  )
  if not match:
    raise ValueError("ATPA_VOLUMES section not found in the text")
  block = match.group(1)

  # Split the block into the three tables
  tables = re.split(r"-{5,}\n", block)
  # Remove empty strings and strip whitespace
  tables = [t.strip() for t in tables if t.strip()]
  if len(tables) < 3:
    raise ValueError("Expected three tables in ATPA_VOLUMES section")

  # Parse main volume table
  volume_lines = [line for line in tables[1].splitlines() if line.startswith("|") and not line.startswith("|#")]
  # Parse dimension table
  dim_lines = [line for line in tables[3].splitlines() if line.startswith("|") and not line.startswith("|#")]

  volumes = []
  for v_line, d_line in zip(volume_lines, dim_lines):
    v_fields = [f.strip() for f in v_line.strip().split('|')[1:-1]]
    d_fields = [f.strip() for f in d_line.strip().split('|')[1:-1]]

    if len(v_fields) < 12 or len(d_fields) < 6:
      raise ValueError("Unexpected number of fields in volume or dimension line")

    lat_raw = v_fields[4]
    lon_raw = v_fields[6]

    lat = int(lat_raw[:2]) + int(lat_raw[2:4]) / 60 + int(lat_raw[4:]) / 3600
    if v_fields[5].upper() == "S":
      lat *= -1
    lon = int(lon_raw[:3]) + int(lon_raw[3:5]) / 60 + int(lon_raw[5:]) / 3600
    if v_fields[7].upper() == "W":
      lon *= -1

    volumes.append({
      "id": gen_ulid(),
      "airportId": v_fields[1],
      "volumeId": v_fields[2],
      "name": v_fields[3],
      "runwayThreshold": {"lat": lat, "lon": lon},
      "ceiling": parse_int(v_fields[8]),
      "floor": parse_int(v_fields[11]),
      "magneticHeading": parse_int(v_fields[9]),
      "maximumHeadingDeviation": parse_int(v_fields[10]),
      "length": parse_decimal(d_fields[1]),
      "widthLeft": parse_int(d_fields[2]),
      "twoPointFiveApproachDistance": parse_decimal(d_fields[3]),
      "widthRight": parse_int(d_fields[4]),
      "twoPointFiveApproachEnabled": parse_bool(d_fields[5]),
      "scratchpads": [],
      "tcps": [],
    })
  return volumes


def parse_scratchpads(text):
    scratchpad_block = re.findall(r"ATPA_SCRATCHPAD_ENTRIES \*+\n(.+?)\n\*+", text, re.DOTALL)
    scratchpad_map = defaultdict(list)

    if scratchpad_block:
        for line in scratchpad_block[0].splitlines():
            if not re.match(r"^\|\s*\d+", line):
                continue
            fields = [f.strip() for f in line.strip().split('|') if f.strip()]
            if len(fields) < 6:
                continue
            scratchpad_map[(fields[1], fields[2])].append({
                "id": gen_ulid(),
                "entry": fields[3],
                "scratchPadNumber": "One" if fields[4] == "1" else "Two",
                "type": "Exclude" if fields[5].lower().startswith("exclu") else "Ineligible"
            })

    return scratchpad_map


def parse_tcps(text):
    tcp_block = re.findall(r"ATPA_TCP_DISPLAYS \*+\n(.+?)\n\*+", text, re.DOTALL)
    tcp_map = defaultdict(list)

    if tcp_block:
        for line in tcp_block[0].splitlines():
            if not re.match(r"^\|\s*\d+", line):
                continue
            fields = [f.strip() for f in line.strip().split('|') if f.strip()]
            if len(fields) < 5:
                continue
            tcp_map[(fields[1], fields[2])].append({
                "id": gen_ulid(),
                "tcp": fields[3],
                "coneType": "Alert" if fields[4].lower() == "alert" else "AlertAndMonitor"
            })

    return tcp_map


def combine(volumes, scratchpad_map, tcp_map):
    for vol in volumes:
        key = (vol["airportId"], vol["volumeId"])
        if key in scratchpad_map:
            vol["scratchpads"] = scratchpad_map[key]
        if key in tcp_map:
            vol["tcps"] = tcp_map[key]
    return volumes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert ATPA TXT to JSON")
    parser.add_argument("input_txt_file", help="Input ATPA .txt file")
    parser.add_argument("output_file", help="Output JSON file")

    args = parser.parse_args()

    with open(args.input_txt_file, "r", encoding="utf-8") as f:
        txt = f.read()

    volumes = parse_volume_blocks(txt)
    scratchpads = parse_scratchpads(txt)
    tcps = parse_tcps(txt)
    final = combine(volumes, scratchpads, tcps)

    with open(args.output_file, "w") as f:
        json.dump(final, f, indent=2)

    print(f"Converted {len(final)} volumes to {args.output_file}")
