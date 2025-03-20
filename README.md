# VAKE
Waypoint calculations for VAKE

## What is this tool about
Welcome to VAKE waypoint tool. With this tool, you can extract the waypoints from the provided PDF file and write them to a JSON file.
You can also convert this generated JSON file with UTM coordinates to a GPX file with longitude and latitude coordinates.
The description of the waypoints is included.

> **Important:** There is no guarantee that the tool works correctly! If you use this tool, it is crucial to manually double-check all values!

## How to use this tool

### Clone or download this repository

### Install Python 3.11.9 or later and check the version

```bash
python --version
```

### Upgrade `pip` with the following command

```bash
python -m pip install --upgrade pip
```

### Install Poetry via pip

```bash
pip install poetry
```

### Install Dependencies using Poetry
Navigate to the project directory and install dependencies using `poetry`:

```bash
poetry install
```


### Running the VAKE PDF parser tool
Copy the VAKE waypoint pdf into the project directory.

If you are using a virtual environment managed by Poetry, activate it first:

```bash
poetry shell
```

Then, run the script and pass the source pdf file and the target json file:

```bash
python parse_wp_pdf.py [-h] pdf_path json_path
```

Example

```bash
python parse_wp_pdf.py 2025_Waypoints_VAKE.pdf waypoints.json
```

### Running the waypoint converter tool
Once you have generated a waypoint json file with the VAKE PDF parser tool, you can use this json file to generate a gpx file containing waypoints in latitude and longitude format.

If you are using a virtual environment managed by Poetry, activate it first if not done already:

```bash
poetry shell
```

Then, run the script and pass the source pdf file and the target json file:

```bash
python convert_wp_json.py [-h] json_path gpx_path
```

Example

```bash
python convert_wp_json.py waypoints.json waypoints.gpx
```

### Show the waypoints on a map
Once you have generated a gpx file with the VAKE waypoint converter tool, you can use this gpx file to display the waypoints on a map.

If you are using a virtual environment managed by Poetry, activate it first if not done already:

```bash
poetry shell
```

Then, run the script and pass the source pdf file and the target json file:

```bash
python show_wp.py [-h] [-o OUTPUT] gpx_file
```

Example

```bash
python show_wp.py waypoints.gpx
```

### Batch scripts for VAKE 2025
To make the whole process easier to execute you can use the following scripts

Windows
```bash
2025_process_wp.bat
```

Mac / Linux
```bash
2025_process.sh
```

## Contributing
Feel free to contribute by submitting pull requests or reporting issues. Ensure all changes are tested before submitting.

## License
This project is licensed under the MIT License. See `LICENSE` for more details.

