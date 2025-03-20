import os
import re
import json
import pyproj
import argparse
from datetime import datetime, timezone

def convert_utm_to_gpx(json_path, gpx_path=None):
    # 1. Read the JSON file
    with open(json_path, "r", encoding="utf-8") as f:
        waypoints = json.load(f)

    # 2. Prepare GPX header/footer
    gpx_header = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="VAKE waypoint tool" xmlns="http://www.topografix.com/GPX/1/1">
    <metadata>
        <author>
            <name>rippinsail</name>
        </author>
        <time>{timestamp}</time>
    </metadata>
""".format(timestamp=datetime.now(timezone.utc).isoformat())

    gpx_footer = "</gpx>\n"

    wpt_template = """    <wpt lat="{lat:.6f}" lon="{lon:.6f}">
        <name>{name}</name>
        <desc>{desc}</desc>
    </wpt>
"""

    # Build the GPX content in a list
    gpx_content = [gpx_header]

    # 3. Convert each waypoint’s UTM (zone 35 or 36) → WGS84 lat/lon
    for wp in waypoints:
        zone = wp["zone"]
        if zone == 35:
            crs_utm = pyproj.CRS("EPSG:32635")
        elif zone == 36:
            crs_utm = pyproj.CRS("EPSG:32636")
        else:
            raise ValueError(f"Unsupported UTM zone: {zone}. Expected 35 or 36.")

        transformer = pyproj.Transformer.from_crs(crs_utm, pyproj.CRS("EPSG:4326"), always_xy=True)
        lon, lat = transformer.transform(wp["easting"], wp["northing"])

        desc_sanitized = wp["desc"].replace("&", "and")
        gpx_content.append(
            wpt_template.format(lat=lat, lon=lon, name=wp["name"], desc=desc_sanitized)
        )

    gpx_content.append(gpx_footer)
    gpx_output = "".join(gpx_content)

    # 4. Determine GPX filename
    if gpx_path:
        filename = gpx_path
    else:
        # Use auto-naming scheme if no file is specified
        pattern = re.compile(r"^VAKE_2025_(\d{2})(?:_\d{4}-\d{2}-\d{2})?\.gpx$")
        base_name = "VAKE_2025_"

        max_num = -1
        last_file_path = None

        # Find highest-numbered existing GPX file
        for fname in os.listdir("."):
            match = pattern.match(fname)
            if match:
                file_num = int(match.group(1))
                if file_num > max_num:
                    max_num = file_num
                    last_file_path = fname

        # If we found a previously created file, compare its contents
        if last_file_path:
            with open(last_file_path, "r", encoding="utf-8") as f:
                old_content = f.read()
            if old_content == gpx_output:
                print(f"No changes from {last_file_path}. No new file created.")
                return

        # If we get here, either no previous file or the contents changed
        new_num = max_num + 1 if max_num >= 0 else 1
        filename = f"{base_name}{new_num:02d}.gpx"

    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(gpx_output)

    print(f"Created new file: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert waypoints from JSON (UTM format) to GPX.")
    parser.add_argument("json_path", help="Path to the JSON file containing waypoints.")
    parser.add_argument("gpx_path", default=None, help="Optional: Path to save the output GPX file.")

    args = parser.parse_args()
    convert_utm_to_gpx(args.json_path, args.gpx_path)
