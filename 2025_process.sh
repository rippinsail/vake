#!/bin/bash

# Enable error handling: stops execution if a command fails
set -e

echo "[1/3] Extracting waypoints from PDF..."
python parse_wp_pdf.py 2025_Waypoints_VAKE.pdf 2025_waypoints.json
echo "✔ Successfully extracted waypoints."

echo "[2/3] Converting JSON to GPX..."
python convert_wp_json.py 2025_waypoints.json 2025_waypoints.gpx
echo "✔ Successfully converted waypoints to GPX."

echo "[3/3] Displaying waypoints on map..."
python show_wp.py 2025_waypoints.gpx -o 2025_map.html
echo "✔ Successfully created the waypoint map."

echo "✅ Process completed successfully!"

# Prevent the script from closing immediately if run by double-clicking
read -p "Press Enter to exit..."
