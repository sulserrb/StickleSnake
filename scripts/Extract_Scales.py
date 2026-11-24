
import os
import json
import csv
import argparse

# Directory containing the JSON files
#input_directory = '/mnt/z/BenSulser/2D_Morpho_Stickleback/Stickleback_2021/failed_scales_two/data/measurements/'  # Update this path to your directory
# Output CSV file
#output_file = '/mnt/z/BenSulser/2D_Morpho_Stickleback/2021_specimen_scales_green_two.csv'  # Update this path to your desired output file

def extract_scales(input_directory: str, output_file: str) -> None:
    specimen_scales = {} #dictionary instead of list
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                reference_data = data.get('reference', {})
                key = next(iter(reference_data), None)
                if key:
                    reference_scale = reference_data[key].get('data', {}).get('reference', [None])[0]
                    #Check for degree of mag difference between reference scale and measured scale
                #    measured_scale = data.get('scale', {}).get('data', {}).get('reference', [None])[0]
                #    if reference_scale is not None and measured_scale is not None:
                #        mag_difference = abs(reference_scale - measured_scale) / reference_scale
                #        if mag_difference > 0.2 and mag_difference < 1:  # If the difference is greater than 20% but less than 100%
                #            print(f"Warning: Significant ({mag_difference:.2%}) difference between reference and measured scale for {filename}. Reference: {reference_scale}, Measured: {measured_scale}")
                #        elif mag_difference > 2:  # If the difference is greater than 100  
                #            print(f"Error: Excessive difference between reference and measured scale for {filename}. Reference: {reference_scale}, Measured: {measured_scale}. Setting to none.")
                #            reference_scale = None  # Set to None to indicate an error
                else: 
                    reference_scale = None
                specimen_name = filename.replace('.json', '').split('_annotation_')[0]

                #Fix to avoid duplicate entries in the CSV file by checking if the specimen already exists in the list
                if specimen_name not in specimen_scales or (specimen_scales[specimen_name] is None and reference_scale is not None):
                    specimen_scales[specimen_name] = reference_scale

        # Write the data to a CSV file
    with open(output_file, 'w', newline='') as csv_file:
        fieldnames = ['specimen', 'scale']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for specimen, scale in specimen_scales.items():
            writer.writerow({'specimen': specimen, 'scale': scale})





def main(argv=None):
    p = argparse.ArgumentParser(description='Extract scales from JSON files and write to CSV')
    p.add_argument('--input_dir', required=True, help='Directory containing JSON files')
    p.add_argument('--output_csv', required=True, help='Output CSV file path') 
    args = p.parse_args(argv)       

    extract_scales(args.input_dir, args.output_csv)

    print(f'Data has been written to {args.output_csv}')

if __name__ == "__main__":
    main()  