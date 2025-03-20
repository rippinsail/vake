@echo off
REM Windows batch script to process waypoints
REM Stops execution if any command fails
setlocal enabledelayedexpansion

echo [1/3] Extracting waypoints from PDF...
python parse_wp_pdf.py 2025_Waypoints_VAKE.pdf 2025_waypoints.json
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to extract waypoints from PDF.
    exit /b %ERRORLEVEL%
)

echo [2/3] Converting JSON to GPX...
python convert_wp_json.py 2025_waypoints.json 2025_waypoints.gpx
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to convert waypoints JSON to GPX.
    exit /b %ERRORLEVEL%
)

echo [3/3] Displaying waypoints on map...
python show_wp.py 2025_waypoints.gpx -o 2025_map.html
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to display waypoints.
    exit /b %ERRORLEVEL%
)

echo Process completed successfully!

REM Prevent the script from closing immediately if double-clicked
pause
