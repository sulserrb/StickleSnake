#Program should: 

#Apply a template to images in a folder, measure them, extract scales, list failed specimens, and move them to a new folder. Repeat for multiple templates if necessary.
#This iteration should try multiple templates per one specimen, instead of running a new iteration for each template.

import os
import argparse
import fnmatch

from measure_light_new import check_temp as measure
from Extract_Scales import extract_scales as extract
from List_Failed_Scale import extract_scale_from_csv as list_failed
from List_Failed_Scale import copy_failed_specimens as move


def check_templates_annotations(starting_templates,template_dir):
   templates = [file for file in starting_templates]
   annotations = [file for file in os.listdir(template_dir) if file.endswith('.json') and file.startswith('annotation_')]

   # Create a set of base names for templates and annotations
   template_bases = {os.path.splitext(file)[0].replace('template_', '') for file in templates}
   annotation_bases = {os.path.splitext(file)[0].replace('annotation_', '') for file in annotations}

    # Check for missing annotations for each template
   missing_annotations = []
   found_templates = []
   for template_base in template_bases:
      if template_base not in annotation_bases:
         missing_annotations.append(template_base)
         template_bases.remove(template_base)  # Remove the template without a corresponding annotation
      else:
         found_templates.append(template_base)

   if missing_annotations:
      print(f"Warning: Missing annotation files for the following templates: {', '.join(missing_annotations)}")
      print("Removing templates without corresponding annotations.")
      print("Please ensure that each template has a corresponding annotation JSON file.")
      return found_templates  # Return only templates that have corresponding annotations
   return found_templates  # Return all templates if no missing annotations


# a simple to handle ignore patterns, normalizing them to lower case and adding wildcards if necessaryS
def normalize_ignore_patterns(tokens):
   if tokens is None:
      return []
   if isinstance(tokens, str):
      tokens = [tokens]

   patterns = []
   for token in tokens:
      t = token.strip().lower()
      if not t:
         continue
      if not any(ch in t for ch in "*?["):
         t = f"*{t}*"
      patterns.append(t)
   return patterns


# A simple function to check if a filename matches any of the ignore patterns
def ignore_files(filename, ignore_string):
   name = filename.lower()
   return any(fnmatch.fnmatch(name, pattern.lower()) for pattern in ignore_string)

def try_measure_with_templates(image_path, template_bases, output_dir, template_dir):
   #Initialize
   remaining_templates = template_bases.copy()

   #Error handling for no templates
   if not remaining_templates:
      print(f"No templates found in {template_dir}. Please ensure that template images are present.")
      return

   while remaining_templates:
      template = remaining_templates.pop(0)
      template_path = os.path.join(template_dir, f"template_{template}.png")  
      annotation_path = os.path.join(template_dir, f"annotation_{template}.json")    # Remove the first part before the last underscore and add .json
      #Try measuring with each template until one succeeds
      measurement_result = measure(image_path, template_path, annotation_path, output_dir=output_dir)
      if measurement_result == 1:
         print(f"Measurement failed for {image_path} using template {template_path}.")
         if not remaining_templates:
            print(f"No more templates to try for {image_path}.")
            break
      else:
         print(f"Measurement succeeded for {image_path} using template {template_path}.")
         break

def main(argv=None):
    # Define the paths for the input image, template, annotation, and output files
   p = argparse.ArgumentParser(description='Run the full workflow: measure specimens, extract scales, list failed specimens, and move them to a new folder, repeating for multiple templates if necessary.')
   p.add_argument('--input_dir', required=True, help='Directory containing uncropped images to be measured')
   p.add_argument('--template_dir', required=True, help='Directory containing template images')
   p.add_argument('--output_root', required=True, help='Root directory for output files and folders')
   p.add_argument('--ignore_string',required=False, default=None, action='append', help='List of strings to ignore in the filenames when processing')
   p.add_argument('--output_csv', required=False, default="detected_scales.csv", help='Path to the output CSV file for detected scales')
   args = p.parse_args(argv)

   # Normalize the ignore patterns

   
   ignore_tokens = args.ignore_string or []  # always a list, even if empty
   print(f"Ignore patterns: {ignore_tokens}")
   args.ignore_string = normalize_ignore_patterns(ignore_tokens)
   input_dir = args.input_dir
   template_dir = args.template_dir
   output_root = args.output_root
   starting_templates = [file for file in os.listdir(template_dir) if file.endswith('.png')]


   #Check for missing annotation files corresponding to the templates
   template_bases = check_templates_annotations(starting_templates, template_dir)

   if not template_bases:
      print("No valid templates with corresponding annotations found. Exiting.") 
      exit(1)
      

   output_dir=os.path.join(output_root, f"measurements_{len(template_bases)}_templates")
   if not os.path.exists(output_dir):
      os.makedirs(output_dir)

   # Step 1: Measure the specimens in a directory using the template and matching annotation. 
   for image_file in os.listdir(input_dir):
      if image_file.lower().endswith(('.png', '.jpg', '.jpeg')) and not ignore_files(image_file, args.ignore_string):
         image_path = os.path.join(input_dir, image_file)
         try_measure_with_templates(image_path, template_bases, output_dir, template_dir)

   # Step 2: Extract scales from the JSON files and write to CSV
   output_csv = args.output_csv
   extract(output_dir, output_csv)


if __name__ == "__main__":
   main()
