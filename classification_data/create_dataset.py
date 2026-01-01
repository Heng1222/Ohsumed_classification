
import os
import csv
import sys

def create_dataset(root_dir, output_file):
    """
    Scans subdirectories of a root directory to create a CSV dataset.

    Each subdirectory is treated as a category (label). Each file within a 
    subdirectory is a data sample, and its content is the feature (text).

    Args:
        root_dir (str): The path to the root directory containing category subdirectories.
        output_file (str): The name of the CSV file to be created.
    """
    # Check if the root directory exists
    if not os.path.isdir(root_dir):
        print(f"Error: Root directory '{root_dir}' not found.")
        sys.exit(1)

    data_records = []
    print("Starting dataset creation...")

    # Get sorted list of directories to ensure consistent order
    try:
        category_dirs = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d.startswith('C')])
    except OSError as e:
        print(f"Error accessing directory {root_dir}: {e}")
        sys.exit(1)

    if not category_dirs:
        print(f"No category directories (like C01, C02, ...) found in '{root_dir}'.")
        sys.exit(1)

    # Iterate through each category directory
    for category in category_dirs:
        label = category
        category_path = os.path.join(root_dir, category)
        print(f"Processing directory: {category_path} as label '{label}'")
        
        try:
            files_in_dir = os.listdir(category_path)
            file_count = len(files_in_dir)
            
            # Process each file in the category directory
            for i, filename in enumerate(files_in_dir):
                file_path = os.path.join(category_path, filename)
                
                # Print progress for large directories
                if file_count > 1000 and (i + 1) % 500 == 0:
                    print(f"  ...processed {i + 1}/{file_count} files in '{category}'")

                if os.path.isfile(file_path):
                    try:
                        # Using 'latin-1' as it's a common fallback for older text datasets
                        with open(file_path, 'r', encoding='latin-1') as f:
                            # The first line is the title
                            title = f.readline().strip()
                            # The rest of the content is the abstract
                            abstract = f.read().strip()
                        
                        # Append the record to our list if both title and abstract have content
                        if title and abstract:
                            data_records.append({'title': title, 'abstract': abstract, 'label': label})

                    except (IOError, UnicodeDecodeError) as e:
                        print(f"  - Warning: Could not read or decode file {file_path}. Error: {e}")
            print(f"  -> Found and processed {file_count} files.")

        except OSError as e:
            print(f"  - Warning: Could not access files in {category_path}. Error: {e}")


    # Check if any data was collected
    if not data_records:
        print("No data was collected. The output file will not be created.")
        return

    # Write the collected data to a CSV file
    print(f"\nWriting {len(data_records)} records to {output_file}...")
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            # Define column headers
            fieldnames = ['title', 'abstract', 'label']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header
            writer.writeheader()
            
            # Write data rows
            writer.writerows(data_records)
        
        print(f"Successfully created dataset: {output_file}")

    except IOError as e:
        print(f"Error writing to file {output_file}. Error: {e}")


if __name__ == '__main__':
    # The script assumes it's run from the 'ohsumed-all' directory's parent,
    # or you can specify the path directly.
    # We'll use '.' to indicate the current directory based on your context. 
    current_directory = '.' 
    csv_filename = 'ohsumed_dataset.csv' # Corrected from 'ohsumed_dataset.csv'
    
    create_dataset(current_directory, csv_filename)
