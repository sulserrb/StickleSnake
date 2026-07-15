from sklearn.model_selection import KFold

#kf = KFold(n_splits=5, shuffle=True, random_state=42)
#for train_idx, test_idx in kf.split(filenames):
#    train_set = [filenames[i] for i in train_idx]
#    test_set = [filenames[i] for i in test_idx]

#Integrate into the utils! Add a flag, and a small portion to it 

def split_train_test_kfold(input_dir, output_dir = "data", kfold=5): 
    '''
    Splits an image directory into 'train' and 'test' directories. The original image directory is preserved. 
    When creating the new directories, this function converts all image files to 'jpg'. The function returns
    a dictionary containing the image dimensions in the 'train' and 'test' directories.
    
    Parameters:
        input_dir(str)=original image directory
        output_dir(str)= name of the output directory where the 'train' and 'test' directories will be created. The default is 'data'.
        kfold(int)= number of folds for KFold cross-validation. The default is 5.
        
    Returns:
        sizes (dict): dictionary containing the image dimensions in the 'train' and 'test' directories.
    '''
    # Listing the filenames.Folders must contain only image files (extension can vary).Hidden files are ignored
    filenames = os.listdir(input_dir)
    filenames = [os.path.join(input_dir, f) for f in filenames if not f.startswith('.')]

    # Splitting the images into 'train' and 'test' directories (80/20 split)
    random.seed(845)
    filenames.sort()
    random.shuffle(filenames)
    split = int(0.8 * len(filenames))
    train_set = filenames[:split]
    test_set = filenames[split:]

    kf = KFold(n_splits=kfold, shuffle=True, random_state=42)
    for train_idx, test_idx in kf.split(filenames):
        train_set = [filenames[i] for i in train_idx]
        test_set = [filenames[i] for i in test_idx]

    #DEBUGGING
    print("Train set: {} images".format(len(train_set)))
    print("Test set: {} images".format(len(test_set)))

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
    #return sizes

def image_prep(file, name, dir_path):
    '''
    Internal function used by the split_train_test function. Reads the original image files and, while 
    converting them to jpg, gathers information on the original image dimensions. 
    
    Parameters:
        file(str)=original path to the image file
        name(str)=basename of the original image file
        dir_path(str)= directory where the image file should be saved to
        
    Returns:
        file_sz(array): original image dimensions
    '''
    img = cv2.imread(file)
    if img is None:
        print('File {} was ignored, returning None'.format(file))
    #additions to file handling
        file_sz = None
    else:
        file_sz= [img.shape[0],img.shape[1]]
        cv2.imwrite(os.path.join(dir_path,name), img)
    return file_sz