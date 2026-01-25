"""
This script converts the master CSV files from Dataset/Vizwiz-Data/ 
into the format needed by the training scripts.

INPUT: 
- Dataset/Vizwiz-Data/master_data_train.csv
- Dataset/Vizwiz-Data/master_data_val.csv
- Dataset/Vizwiz-Data/master_data_test.csv

OUTPUT (in scripts/ directory):
- train_qual_dist.csv
- val_qual_dist.csv
- test_qual_dist.csv
"""

import pandas as pd
import sys
import os

# Change to scripts directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def create_training_csv(master_csv_path, output_csv_name):
    """
    Convert master CSV to training CSV format
    
    Input columns: image, img_qual, img_dist, ...
    Output columns: image, qual_mos, dist_prob
    
    Where:
    - image: image filename (without extension)
    - qual_mos: image quality score (from img_qual)
    - dist_prob: distortion probabilities (from img_dist)
    """
    
    print(f"Reading: {master_csv_path}")
    df = pd.read_csv(master_csv_path)
    
    # Create new dataframe with only needed columns
    output_df = pd.DataFrame()
    
    # Column 1: image name (just the filename)
    output_df['image'] = df['image'].astype(str)
    
    # Column 2: quality score (quality MOS)
    output_df['qual_mos'] = df['img_qual'].astype(float)
    
    # Column 3: distortion probabilities (keep as string representation of list)
    output_df['dist_prob'] = df['img_dist'].astype(str)
    
    # Save to file
    output_df.to_csv(output_csv_name, index=False)
    print(f"Created: {output_csv_name}")
    print(f"Rows: {len(output_df)}")
    print(f"Columns: {list(output_df.columns)}\n")
    
    return output_df

# Create the training CSVs
print("=" * 60)
print("Creating Training CSVs from Master Data")
print("=" * 60)
print()

# Train CSV
train_df = create_training_csv(
    '../Dataset/Vizwiz-Data/master_data_train.csv',
    'train_qual_dist.csv'
)

# Validation CSV
val_df = create_training_csv(
    '../Dataset/Vizwiz-Data/master_data_val.csv',
    'val_qual_dist.csv'
)

# Test CSV
test_df = create_training_csv(
    '../Dataset/Vizwiz-Data/master_data_test.csv',
    'test_qual_dist.csv'
)

print("=" * 60)
print("Summary:")
print("=" * 60)
print(f"Training samples:   {len(train_df)}")
print(f"Validation samples: {len(val_df)}")
print(f"Test samples:       {len(test_df)}")
print()
print("✓ All CSVs created successfully!")
print()
print("Next steps:")
print("1. Make sure your images are in: ../vizwiz/train/, ../vizwiz/val/, ../vizwiz/test/")
print("2. Run the training script: python mliqa_resnet50_tf.py my_model 10 0.001")
print("   (or use mliqa_mobilenet_tf.py, mliqa_xception_tf.py, etc.)")