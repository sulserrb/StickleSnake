'''
Script needs to: read in all generated model/landmark_model_{fold}_metrics.csv files, summarize the results, and output a single summary CSV file with the following columns: model_name, train_error, test_error, and any other relevant metrics. 
The script should also generate, from data/output/results_table_fold_{fold}.tex files, the landmark with the best and worst performance and the worst-performing image. 
All results should then be generated into a LaTeX table and saved to data/output/fold_summary_table.tex.

INPUTS:
- input_files: List of fold files to summarize

OUTPUTS:
-  output_file: Path to the output LaTeX file
'''


import argparse
import re
from astropy.table import Table
import pandas as pd
import os



def main():
    parser = argparse.ArgumentParser(description="Summarize fold results and generate LaTeX table.")

    parser.add_argument("--input_files", nargs="+", required=True)
    parser.add_argument("--output_file", type=str, default="data/output/fold_summary_table.tex", help="Output LaTeX file path.")
    args = parser.parse_args()
    
    metrics_files = {}
    results_files = {}

    for p in args.input_files:
        m1 = re.search(r"landmark_model_(\d+)_metrics\.csv$", p)
        m2 = re.search(r"results_table_fold_(\d+)\.tex$", p)
        if m1:
            metrics_files[int(m1.group(1))] = p
        elif m2:
            results_files[int(m2.group(1))] = p

    common_folds = sorted(set(metrics_files) & set(results_files))
    output_file = args.output_file      

    # Initialize lists to store metrics
    model_names = []
    train_errors = []
    test_errors = []
    best_landmarks = []
    worst_landmarks = []
    worst_images = []

    for fold in common_folds:
        #initialize file paths for metrics and results
        metrics_file = metrics_files[fold]
        results_file = results_files[fold]

        if os.path.exists(metrics_file):
            #Read metrics CSV, extract train and test errors, and append to lists
            print(f"Reading metrics for fold {fold}: {metrics_file}")
            metrics_df = pd.read_csv(metrics_file)
            model_names.append(f"landmark_model_{fold}")
            #print(metrics_df) #DEBUG: Print the metrics DataFrame to verify its contents
            train_errors.append(metrics_df['Value'].values[0])
            test_errors.append(metrics_df['Value'].values[1])
        else:
            #Error handling if metrics file is missing
            print(f"Metrics file not found for fold {fold}: {metrics_file}")
            continue

        if os.path.exists(results_file):
            #Read results CSV, find best/worst landmarks and worst image, and append to lists
            print(f"Reading results for fold {fold}: {results_file}")
            results_df = Table.read(results_file, format='latex').to_pandas()
            print(results_df) #DEBUG: Print the results DataFrame to verify its contents
            best_landmark_row = results_df.loc[results_df['mean'].idxmin()]
            worst_landmark_row = results_df.loc[results_df['mean'].idxmax()]
            worst_image = results_df['worst outlier image'].value_counts().idxmax()

            best_landmarks.append(best_landmark_row['Landmark'])
            worst_landmarks.append(worst_landmark_row['Landmark'])
            
            worst_images.append(worst_image)
            print(f"Heads-up: if there is a tie in scores for worst image selection, the first one found will be used: {worst_image}")
        else:
            #Error handling if results file is missing
            print(f"Results file not found for fold {fold}: {results_file}")
            continue

    # Create summary DataFrame
    summary_df = pd.DataFrame({
        'model_name': model_names,
        'train_error': train_errors,
        'test_error': test_errors,
        'best_landmark': best_landmarks,
        'worst_landmark': worst_landmarks,
        'worst_image': worst_images
    })

    # Save summary to LaTeX table
    print(f"Saving summary to LaTeX table: {output_file}")
    with open(output_file, 'w') as f:
        f.write(summary_df.to_latex(index=False))

if __name__ == "__main__":
    main()