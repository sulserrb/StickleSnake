from sklearn.model_selection import KFold
import argparse
import utils
import os
import random

def split_train_test_kfold(input_dir, output_dir = "data", kfold=5): 
    '''
    Splits an image directory into 'train' and 'test' text files. The original image directory is preserved. 
    When creating the new directories, this function converts all image files to 'jpg'. The function returns
    a text files with intended file names for all 'train' and 'test' directories for all kfold runs
    
    Parameters:
        input_dir(str)=original image directory
        output_dir(str)= name of the output directory where the 'train' and 'test' directories will be created. The default is 'data'.
        kfold(int)= number of folds for KFold cross-validation. The default is 5.
        
    Returns:
        sizes (dict): dictionary containing the image dimensions in the 'train' and 'test' directories.
    '''
    # Listing the filenames.Folders must contain only image files (extension can vary).Hidden files are ignored. 

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".gif", ".webp", ".JPG"}

    filenames = os.listdir(input_dir)
    filenames = [os.path.join(input_dir, f) for f in filenames if not f.startswith('.') and any(f.endswith(ext) for ext in IMAGE_EXTENSIONS)]

    # Splitting the images into 'train' and 'test' directories (80/20 split)
    random.seed(845)
    filenames.sort()

    kf = KFold(n_splits=kfold, shuffle=True, random_state=42)
    print(kf)
    
    for i, (train_idx, test_idx) in enumerate(kf.split(filenames)):
        print(f"Writing Fold {i+1}:")
        train_set = [filenames[i] for i in train_idx]
        test_set = [filenames[i] for i in test_idx]
        if not os.path.exists(f"data/output/fold{i+1}"):
            os.mkdir(f"data/output/fold{i+1}")
        f = open(f"data/output/fold{i+1}/train.txt", "w")
        for item in train_set:
            f.write("%s\n" % item)
        f.close()
        f = open(f"data/output/fold{i+1}/test.txt", "w")
        for item in test_set:
            f.write("%s\n" % item)
        f.close() 
        print(f"Fold {i+1} written with {len(train_set)} training images and {len(test_set)} testing images in data/output/fold{i+1}/train.txt and data/output/fold{i+1}/test.txt respectively.")
        #print(f"Train indices: {train_idx}")
        #print(f"Test indices: {test_idx}"
    #DEBUGGING
    #print("Train set: {} images".format(len(train_set)))
    #print("Test set: {} images".format(len(test_set)))
    return

    filenames = {'train':train_set,
                 'test': test_set}
    sizes={}
    for split in ['train','test']:
        sizes[split]={}
        split_dir = os.path.join(output_dir, split)
        if not os.path.exists(split_dir):
            os.mkdir(split_dir)
        else:
            print("Warning: the folder {} already exists. It's being replaced".format(split_dir))
            shutil.rmtree(split_dir)
            os.mkdir(split_dir)

        for filename in filenames[split]:
            basename=os.path.basename(filename)
            name=os.path.splitext(basename)[0] + '.jpg'
            sizes[split][name]=image_prep(filename,name,split_dir)
    return 
def main():
    args = vars(ap.parse_args())

    print("starting now!")

    assert os.path.isdir(args['input_dir']), "Could not find the folder {}".format(args['input_dir'])

    split_train_test_kfold(args['input_dir'], kfold=args['kfold'])


ap = argparse.ArgumentParser()
ap.add_argument('-i','--input-dir', type=str, default='images', help="input directory containing image files (default = images)", metavar='')
ap.add_argument('-c','--csv-file', type=str, default=None, help="(optional) XY coordinate file in csv format", metavar='')
ap.add_argument('-t','--tps-file', type=str, default=None, help="(optional) tps coordinate file", metavar='')
ap.add_argument('-k','--kfold', type=int, default=5, help="Use KFold cross-validation to split the dataset into train and test sets (default = 5)", metavar='')

if __name__ == "__main__":
    main()