import os
from pathlib import Path
import shutil
import argparse
from sys import argv


#Function to extract scale from .csv file created as the output of Extract_Scales.py
def extract_scale_from_csv(csv_file_path):
    names = []
    with open(csv_file_path, 'r') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 2:
                specimen, scale = parts
                if parts[1].lower() == '':
                    print (f"Empty scale found for {specimen}: {scale}")
                    names.append(specimen)
    return names


def copy_failed_specimens(failed_specimens, root_directory, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    source_folder = root_directory
    for specimen in failed_specimens:
        source_path_jpg = os.path.join(source_folder, f"{specimen}.jpg")
        source_path_JPG = os.path.join(source_folder, f"{specimen}.JPG")
        print(f"Debugging: Found {specimen} in {source_folder}, copying to {destination_folder}")
        print(f"Debugging: Checking specimen for white spaces: {repr(specimen)}")
        if os.path.exists(source_path_jpg):
            source_path = source_path_jpg
            destination_name = f"{specimen}.jpg"
        elif os.path.exists(source_path_JPG):
            source_path = source_path_JPG
            destination_name = f"{specimen}.JPG"
        else:
            print(f"NOT FOUND: {specimen} in {source_folder} (checked {source_path_jpg} and {source_path_JPG})")
            continue
            

        destination_path = os.path.join(destination_folder, destination_name)
        shutil.copyfile(source_path, destination_path)
        print(f"Copied {specimen} to {destination_folder}")



def copy_failed_specimens_lakes(failed_specimens, root_directory, lakes, year, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    for lake in lakes:
        source_folder = os.path.join(root_directory, f"{lake}_{year}")
        print(f"Debugging: Checking lake {lake} in folder {source_folder}")



        for specimen in failed_specimens:
            source_path_jpg = os.path.join(source_folder, f"{specimen}.jpg")
            source_path_JPG = os.path.join(source_folder, f"{specimen}.JPG")
            if os.path.exists(source_path_jpg):
                source_path = source_path_jpg
                destination_name = f"{specimen}.jpg"
            elif os.path.exists(source_path_JPG):
                source_path = source_path_JPG
                destination_name = f"{specimen}.JPG"
            else:
                continue
            
            #print(f"Debugging: Found {specimen} in {source_folder}, copying to {destination_folder}")
            destination_path = os.path.join(destination_folder, destination_name)
            shutil.copyfile(source_path, destination_path)
            print(f"Copied {specimen} to {destination_folder}")


def main():
    p = argparse.ArgumentParser(description='List specimens that failed scale extraction and copy their images to a new folder')
    p.add_argument('--csv_path', required=True, help='Path to the CSV file')
    p.add_argument('--root_directory', required=True, help='Root directory containing the image folders')
    p.add_argument('--output_directory', required=True, help='Output directory for failed specimens')
    p.add_argument('--Year', required=False, help='Last digits for year of the specimens (e.g., 23)') 
    args = p.parse_args()

    #print("Debugging: Starting main function")
    failed_specimens = extract_scale_from_csv(args.csv_path)
    if not failed_specimens:
        print("No failed specimens found in the CSV file.")
        return
    with open(f"{args.output_directory}/failed_scales.txt", 'w') as f:
        for specimen in failed_specimens:
            f.write(specimen + '\n')
    print(f"Extracted {len(failed_specimens)} failed specimens. List saved to failed_scales.txt")

    if args.Year:
        copy_failed_specimens_lakes(failed_specimens, args.root_directory, lakes, args.Year, args.output_directory)
    else:
        copy_failed_specimens(failed_specimens, args.root_directory, args.output_directory)


if __name__ == "__main__":
    main()
