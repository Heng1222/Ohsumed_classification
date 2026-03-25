
import os
import csv
import sys
import pandas as pd
def load_ohsumed_data(data_dir, split="training"):
    """
    Parse Ohsumed folder structure.
    Default structure: data_dir/training/category_folder/text_file
    """
    split_dir = os.path.join(data_dir, split)
    texts = []
    labels = []

    # Dynamically create category mapping (0 to 22)
    categories = sorted(os.listdir(split_dir))
    category_to_id = {cat: idx for idx, cat in enumerate(categories) if os.path.isdir(os.path.join(split_dir, cat))}

    for cat, label_id in category_to_id.items():
        cat_dir = os.path.join(split_dir, cat)
        for filename in os.listdir(cat_dir):
            filepath = os.path.join(cat_dir, filename)
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    texts.append(f.read())
                labels.append(label_id)

    return texts, labels
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
    train_texts, train_labels = load_ohsumed_data(root_dir, split="training")
    test_texts, test_labels = load_ohsumed_data(root_dir, split="test")
    df_train = pd.DataFrame({"abstract": train_texts, "label": train_labels})
    df_test = pd.DataFrame({"abstract": test_texts, "label": test_labels})
    df = pd.concat([df_train, df_test], ignore_index=True)
    df = df.loc[~df.duplicated(subset='abstract', keep=False)]
    # Check if any data was collected
    if not len(df):
        print("No data was collected. The output file will not be created.")
        return

    # Write the collected data to a CSV file
    print(f"\nWriting {len(df)} records to {output_file}...")
    try:
        df.to_csv(output_file, index=False)
        print(f"Successfully created dataset: {output_file}")

    except IOError as e:
        print(f"Error writing to file {output_file}. Error: {e}")


if __name__ == '__main__':
    # The script assumes it's run from the 'ohsumed-all' directory's parent,
    # or you can specify the path directly.
    # We'll use '.' to indicate the current directory based on your context. 
    current_directory = './ohsumed-first-20000-docs' 
    csv_filename = 'ohsumed_dataset.csv' # Corrected from 'ohsumed_dataset.csv'
    
    create_dataset(current_directory, csv_filename)
