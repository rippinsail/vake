import pdfplumber
import json
import re
import argparse

def extract_waypoints_from_pdf(pdf_path):
    """
    Parses pages 2 and 3 (pdf.pages[1], pdf.pages[2]) of a PDF containing
    multi-line waypoint data. Each waypoint has:
      - name
      - zone (35 or 36)
      - easting
      - northing
      - desc (accumulated from multi-row partial lines)

    Key improvements for #20, #21, #22:
      * We parse easting & northing incrementally (2 integers at a time),
        so easting can be in one line and northing in the next, and any text
        is kept for 'desc'.
    """

    waypoints = []
    with pdfplumber.open(pdf_path) as pdf:
        # Extract tables from pages 2 & 3
        tables = []
        for page_idx in [1, 2]:
            if page_idx < len(pdf.pages):
                extracted = pdf.pages[page_idx].extract_table()
                if extracted:
                    tables.append(extracted)
                else:
                    print(f"No table found on page {page_idx+1}.")

        # Merge rows from both pages
        all_rows = []
        for i, tbl in enumerate(tables):
            if i == 0 and tbl:
                # skip header row
                data_rows = tbl[1:]
            else:
                data_rows = tbl
            if data_rows:
                all_rows.extend(data_rows)

    # Track current waypoint
    current_wp = None
    found_position = False  # once we find easting & northing, we set this
    partial_text = ""       # text from which we extract integers for e/n

    # ------------------- HELPER FUNCTIONS -------------------

    def remove_coordinate_artifacts(txt):
        """
        Remove leftover 'x ... y' tokens, single x/y, newlines => spaces.
        """
        txt = re.sub(r'[xX]\s*\n*\s*\d+\s*[yY]', '', txt)
        txt = re.sub(r'\b\d+\s*[xX]\b', '', txt)  # Removes cases like '0412680 x'
        txt = re.sub(r'\b[xX]\b', '', txt)
        txt = re.sub(r'\b[yY]\b', '', txt)
        # unify newlines => spaces
        txt = txt.replace('\n', ' ')
        txt = re.sub(r'\s+', ' ', txt).strip()
        return txt

    def append_desc(wp, txt):
        """
        Append text to wp['desc'] after cleaning coordinate remnants and collapsing spaces.
        """
        if not txt.strip():
            return
        clean = remove_coordinate_artifacts(txt)
        if not clean:
            return
        if wp["desc"]:
            wp["desc"] += " " + clean
        else:
            wp["desc"] = clean

    def parse_incremental_coords(txt):
        """
        Extract up to 2 integers from the start of 'txt':
          => (east, north, leftover)
        If fewer than 2, => (None, None, original txt).
        If more than 2 exist, we only consume the first 2 for e/n, and the rest remain leftover.
        """
        nums = re.findall(r'\d+', txt)
        if len(nums) < 2:
            # not enough for e/n
            return None, None, txt
        e_val = int(nums[0])
        n_val = int(nums[1])

        # now we remove only the portion up through the second match
        pattern = r'(\d+).*?(\d+)'
        match = re.search(pattern, txt)
        leftover = txt[match.end(2):].strip() if match else ""
        return e_val, n_val, leftover

    # ------------------- MAIN PARSE LOGIC -------------------
    for row in all_rows:
        # Replace None with '', unify newlines => spaces
        row = [c.replace('\n', ' ').strip() if c else "" for c in row]

        # Check if row[0] & row[1] define a new waypoint
        if row[0] and row[1]:
            # If we had a WP in progress, store it
            if current_wp:
                waypoints.append(current_wp)

            # Start fresh
            current_wp = {
                "name": row[0],
                "zone": None,
                "easting": None,
                "northing": None,
                "desc": ""
            }
            found_position = False
            partial_text = ""

            # Parse zone from row[1], e.g. "WGS84 / 35W" => 35
            zone_match = re.search(r'(\d{2})W', row[1])
            if not zone_match:
                raise ValueError(f"Could not parse zone from '{row[1]}'")
            current_wp["zone"] = int(zone_match.group(1))

            # Everything else on this row might have coords or desc
            tail_cols = row[2:] if len(row) > 2 else []
            merged_tail = " ".join(tc for tc in tail_cols if tc).strip()
            partial_text += (" " + merged_tail).strip()

            # Try extracting coords from partial_text
            e_val, n_val, leftover = parse_incremental_coords(partial_text)
            append_desc(current_wp, leftover)
            if e_val is not None and n_val is not None:
                current_wp["easting"] = e_val
                current_wp["northing"] = n_val
                found_position = True
                # leftover => desc
                #append_desc(current_wp, leftover)
                partial_text = ""
            # else we keep partial_text unmodified (still collecting)

        else:
            # This row is a continuation for the current waypoint
            if not current_wp:
                continue  # skip lines if no WP started

            # Merge all columns into one line
            line = " ".join(c for c in row if c).strip()
            if not line:
                continue

            # If we haven't found coords yet, keep searching
            if not found_position:
                partial_text += " " + line
                partial_text = partial_text.strip()

                e_val, n_val, leftover = parse_incremental_coords(partial_text)
                if e_val is not None and n_val is not None:
                    current_wp["easting"] = e_val
                    current_wp["northing"] = n_val
                    found_position = True
                    # leftover => desc
                    append_desc(current_wp, leftover)
                    partial_text = ""
            else:
                # We already have coords => everything is desc
                append_desc(current_wp, line)

    # After finishing all rows, if a WP is open, store it
    if current_wp:
        waypoints.append(current_wp)

    # Filter out any lacking e/n
    waypoints = [wp for wp in waypoints if wp["easting"] and wp["northing"]]

    return waypoints

def main():
    parser = argparse.ArgumentParser(description="Extract waypoints from VAKE PDF and save them to a JSON file.")
    parser.add_argument("pdf_path", help="Path to the PDF file containing waypoints")
    parser.add_argument("json_path", help="Path to save the extracted waypoints JSON file")

    args = parser.parse_args()

    wpts = extract_waypoints_from_pdf(args.pdf_path)

    with open(args.json_path, "w", encoding="utf-8") as f:
        json.dump(wpts, f, ensure_ascii=False, indent=2)

    print(f"{args.json_path} created successfully!")
    
    
if __name__ == "__main__":
    main()
