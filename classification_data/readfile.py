import pandas as pd
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

# --- Configuration ---
CSV_FILE_PATH = 'ohsumed_dataset.csv'
TRAIN_SET_RATIO = 1
TEST_SET_RATIO = 0.0
RANDOM_STATE = 42  # for reproducibility

def perform_eda(df: pd.DataFrame, dataset_name: str):
    """
    Performs and prints a basic Exploratory Data Analysis (EDA) on the given dataframe.
    Analyzes 'label', 'title', and 'abstract' columns separately.

    Args:
        df (pd.DataFrame): The dataframe to analyze.
        dataset_name (str): The name of the dataset for titles and logging.
    """
    print("\n" + "="*50)
    print(f"  Exploratory Data Analysis (EDA) for: {dataset_name}")
    print("="*50 + "\n")

    # 1. Basic Information
    print(f"[*] Total number of records: {len(df)}")
    if df.empty:
        print("[!] The dataframe is empty. Skipping further analysis.")
        return

    # 2. Label Distribution
    print("\n[*] Label Distribution:")
    if 'label' in df.columns:
        label_counts = df['label'].value_counts()
        print(label_counts)

        # Plotting label distribution
        plt.figure(figsize=(12, 8))
        sns.countplot(y='label', data=df, order=label_counts.index, palette='viridis')
        plt.title(f'Label Distribution in {dataset_name}', fontsize=16)
        plt.xlabel('Count', fontsize=12)
        plt.ylabel('Label', fontsize=12)
        plt.tight_layout()
        plot_filename_labels = f'img/eda_labels_{dataset_name.replace(" ", "_").lower()}.png'
        plt.savefig(plot_filename_labels)
        print(f"\n[+] Saved label distribution plot to: {plot_filename_labels}")
        plt.close()
    else:
        print("[!] 'label' column not found. Skipping label analysis.")


    # 3. Title Length Analysis (in characters)
    print("\n[*] Title Length Analysis (Number of Characters):")
    if 'title' in df.columns:
        df['title_length'] = df['title'].astype(str).apply(len)
        print(df['title_length'].describe())

        # Plotting title length distribution
        plt.figure(figsize=(12, 6))
        sns.histplot(df['title_length'], bins=50, kde=True)
        plt.title(f'Title Length Distribution in {dataset_name}', fontsize=16)
        plt.xlabel('Title Length (Characters)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        plot_filename_length = f'img/eda_title_length_{dataset_name.replace(" ", "_").lower()}.png'
        plt.savefig(plot_filename_length)
        print(f"[+] Saved title length distribution plot to: {plot_filename_length}")
        plt.close()
    else:
        print("[!] 'title' column not found. Skipping title length analysis.")

    # 4. Abstract Length Analysis (in characters)
    print("\n[*] Abstract Length Analysis (Number of Characters):")
    if 'abstract' in df.columns:
        df['abstract_length'] = df['abstract'].astype(str).apply(len)
        print(df['abstract_length'].describe())

        # Plotting abstract length distribution
        plt.figure(figsize=(12, 6))
        sns.histplot(df['abstract_length'], bins=50, kde=True)
        plt.title(f'Abstract Length Distribution in {dataset_name}', fontsize=16)
        plt.xlabel('Abstract Length (Characters)', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.tight_layout()
        plot_filename_length = f'img/eda_abstract_length_{dataset_name.replace(" ", "_").lower()}.png'
        plt.savefig(plot_filename_length)
        print(f"[+] Saved abstract length distribution plot to: {plot_filename_length}")
        plt.close()
    else:
        print("[!] 'abstract' column not found. Skipping abstract length analysis.")


def main():
    """
    Main function to read, split, and analyze the dataset.
    """
    # Check if the CSV file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"Error: The file '{CSV_FILE_PATH}' was not found.")
        print("Please ensure you have run the 'create_dataset.py' script first.")
        sys.exit(1)

    # 1. Read the CSV file
    print(f"Reading data from '{CSV_FILE_PATH}'...")
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Successfully loaded {len(df)} records.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        sys.exit(1)
    
    # 2. Perform EDA on the complete dataset
    perform_eda(df, "Complete Dataset")
    
    print("\n" + "="*50)
    print("EDA process finished. Plots have been saved to PNG files.")
    print("="*50)
    # 欄位預覽
    print_dataset_samples(df)

def print_dataset_samples(df: pd.DataFrame, num_samples: int = 5):
    """
    Prints a few sample records from the dataset for inspection.

    Args:
        df (pd.DataFrame): The dataframe to sample from.
        num_samples (int): Number of samples to print.
    """
    for i in range(num_samples):
        if i < len(df):
            print(f"\nSample Record {i+1}:")
            print(df.iloc[i])
        else:
            break
        
if __name__ == '__main__':
    main()
