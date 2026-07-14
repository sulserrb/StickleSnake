import argparse
import os
import utils
import KFold


ap = argparse.ArgumentParser()
ap.add_argument('-i','--input-dir', type=str, default='images', help="input directory containing image files (default = images)", metavar='')
ap.add_argument('-c','--csv-file', type=str, default=None, help="(optional) XY coordinate file in csv format", metavar='')
ap.add_argument('-t','--tps-file', type=str, default=None, help="(optional) tps coordinate file", metavar='')
ap.add_argument('-k','--kfold', type=bool, default=False, help="(optional) use KFold cross-validation to split the dataset into train and test sets (default = False)", metavar='')

    
args = vars(ap.parse_args())

assert os.path.isdir(args['input_dir']), "Could not find the folder {}".format(args['input_dir'])

#Changed and add Kfold here, adding a new function to import    
if args['kfold']:
    file_sizes=utils.split_train_test_kfold(args['input_dir'])
else:
    file_sizes=utils.split_train_test(args['input_dir'])

if args['csv_file'] is not None:
    dict_csv=utils.read_csv(args['csv_file'])
    utils.generate_dlib_xml(dict_csv,file_sizes['train'],folder='data/train',out_file='data/train.xml')
    utils.generate_dlib_xml(dict_csv,file_sizes['test'],folder='data/test',out_file='data/test.xml')
    utils.dlib_xml_to_tps('data/train.xml')
    utils.dlib_xml_to_tps('data/test.xml')
    
    
    
if args['tps_file'] is not None:
    dict_tps=utils.read_tps(args['tps_file'])
    utils.generate_dlib_xml(dict_tps,file_sizes['train'],folder='data/train',out_file='data/train.xml')
    utils.generate_dlib_xml(dict_tps,file_sizes['test'],folder='data/test',out_file='data/test.xml')
    utils.dlib_xml_to_tps('data/train.xml')
    utils.dlib_xml_to_tps('data/test.xml')
  
