import pandas as pd
from collections import Counter
import os
from dotenv import load_dotenv

load_dotenv()

# Read the CSV file
csv_file = "D:/Projects/trafficlaw-chatbot/data/processed/db_values.csv"
df = pd.read_csv(csv_file)

# Initialize counter
name_counter = Counter()

# Process each entry in file_source column
for value in df['file_source'].dropna():
    # Split by comma and count each name
    names = [name.strip() for name in str(value).split(',') if name.strip()]
    name_counter.update(names)

# Print results
print("Name counts:")
for name, count in name_counter.most_common():
    print(f"{name}: {count}")

print(f"\nTotal unique names: {len(name_counter)}")
print(f"Total occurrences: {sum(name_counter.values())}")