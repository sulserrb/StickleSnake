'''
Script needs to: read in all generated model/landmark_model_{fold}_metrics.csv files, summarize the results, and output a single summary CSV file with the following columns: model_name, train_error, test_error, and any other relevant metrics. 
The script should also generate, from data/output/results_table_fold_{fold}.tex files, the landmark with the best and worst performance and the worst-performing image. 
All results should then be generated into a LaTeX table and saved to data/output/fold_summary_table.tex.

INPUTS:
- model/landmark_model_{fold}_metrics.csv   
- data/output/results_table_fold_{fold}.tex

OUTPUTS:
- data/output/fold_summary_table.tex
'''


import argparse
from astropy.table import Table
import pandas as pd
import os



def main():
    parser = argparse.ArgumentParser(description="Summarize fold results and generate LaTeX table.")
    parser.add_argument("--folds", type=int, required=True, help="Number of folds to summarize.")
    parser.add_argument("--output", type=str, default="data/output/fold_summary_table.tex", help="Output LaTeX file path.")
    args = parser.parse_args()

    folds = args.folds
    output_file = args.output

    # Initialize lists to store metrics
    model_names = []
    train_errors = []
    test_errors = []
    best_landmarks = []
    worst_landmarks = []
    worst_images = []

    for fold in range(folds):
        #initialize file paths for metrics and results
        metrics_file = f"models/landmark_model_{fold}_metrics.csv"
        results_file = f"data/output/results_table_fold_{fold}.tex"

        if os.path.exists(metrics_file):
            #Read metrics CSV, extract train and test errors, and append to lists
            print(f"Reading metrics for fold {fold}: {metrics_file}")
            metrics_df = pd.read_csv(metrics_file)
            model_names.append(f"landmark_model_{fold}")
            train_errors.append(metrics_df['Training Error'].values[0])
            test_errors.append(metrics_df['Testing Error'].values[0])
        else:
            #Error handling if metrics file is missing
            print(f"Metrics file not found for fold {fold}: {metrics_file}")
            continue

        if os.path.exists(results_file):
            #Read results CSV, find best/worst landmarks and worst image, and append to lists
            print(f"Reading results for fold {fold}: {results_file}")
            results_df = Table.read(results_file, format='latex').to_pandas()
            best_landmark_row = results_df.loc[results_df['error'].idxmin()]
            worst_landmark_row = results_df.loc[results_df['error'].idxmax()]
            worst_image_row = results_df.loc[results_df['image_error'].idxmax()]

            best_landmarks.append(best_landmark_row['landmark'])
            worst_landmarks.append(worst_landmark_row['landmark'])
            worst_images.append(worst_image_row['image'])
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