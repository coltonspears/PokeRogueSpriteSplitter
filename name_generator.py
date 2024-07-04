import os
import csv
import argparse
import re

def custom_sort_key(filename):
    # Extract the number from the start of the filename
    match = re.match(r'^(\d+)', filename)
    if match:
        number = int(match.group(1))
    else:
        number = float('inf')  # Place non-numeric names at the end

    # Check if this is a base form (no hyphen)
    is_base_form = '-' not in filename

    # Split the rest of the filename for secondary sorting
    parts = filename.split('-', 1)
    if len(parts) > 1:
        secondary_sort = parts[1].lower()
    else:
        secondary_sort = ''

    # Return a tuple: (number, is base form, secondary sort key)
    return (number, not is_base_form, secondary_sort)

def generate_csv(directory):
    # Get all files in the directory
    all_files = os.listdir(directory)
    
    # Sort the files using the custom sort key
    all_files.sort(key=custom_sort_key)

    # Prepare the output CSV filename
    output_file = "filenames.csv"

    # Write to CSV
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for filename in all_files:
            # Get the filename without extension
            name_without_extension = os.path.splitext(filename)[0]
            # Write the filename (without extension) as a single-item row
            writer.writerow([name_without_extension])

    print(f"CSV file '{output_file}' has been generated with {len(all_files)} entries.")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate a CSV of filenames without extensions, sorted numerically with base forms before variations.")
    parser.add_argument("directory", nargs="?", default=os.getcwd(),
                        help="Directory containing the files (default: current directory)")

    # Parse arguments
    args = parser.parse_args()

    # Use the specified directory or default to current directory
    input_directory = os.path.abspath(args.directory)

    print(f"Processing files in: {input_directory}")
    
    # Generate the CSV
    generate_csv(input_directory)