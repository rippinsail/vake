import folium
import gpxpy
import argparse
import sys
import webbrowser
import os

def generate_map(gpx_file, output_file="map.html"):
    """Reads a GPX file, extracts waypoints, and generates an interactive map with terrain details."""
    
    try:
        with open(gpx_file, "r", encoding="utf-8") as f:
            gpx = gpxpy.parse(f)
    except FileNotFoundError:
        print(f"Error: The file '{gpx_file}' was not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Could not read the GPX file. {e}")
        sys.exit(1)

    # Collect all points (waypoints + track points)
    all_points = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                all_points.append((point.latitude, point.longitude))

    for waypoint in gpx.waypoints:
        all_points.append((waypoint.latitude, waypoint.longitude))

    if not all_points:
        print("Error: GPX file contains no valid waypoints or tracks.")
        sys.exit(1)

    # Determine map center (average location)
    avg_lat = sum(p[0] for p in all_points) / len(all_points)
    avg_lon = sum(p[1] for p in all_points) / len(all_points)
    mymap = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=12,
        tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="OpenTopoMap"
    )

    # Fit the map to include all points
    mymap.fit_bounds(all_points)

    # Add waypoints to the map
    for waypoint in gpx.waypoints:
        folium.Marker(
            location=[waypoint.latitude, waypoint.longitude],
            popup=waypoint.name,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mymap)

    # Save map to an HTML file
    mymap.save(output_file)
    print(f"Map saved as {output_file}. Opening in browser...")

    # Automatically open the file in the default web browser
    webbrowser.open("file://" + os.path.abspath(output_file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an interactive terrain map from a GPX file.")
    parser.add_argument("gpx_file", help="Path to the input GPX file.")
    parser.add_argument("-o", "--output", help="Output HTML file (default: map.html)", default="map.html")

    args = parser.parse_args()
    generate_map(args.gpx_file, args.output)
