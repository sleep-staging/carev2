import os, shutil
import torch
import numpy as np
import argparse

from torch.nn.functional import interpolate

seed = 123
np.random.seed(seed)


parser = argparse.ArgumentParser()

parser.add_argument("--dir", type=str, default="/scratch/shhs_outputs",
                    help="File path to the PSG and annotation files.")

args = parser.parse_args()

## ARGS
half_window = 4
dire = '/scratch/new_shhs_9'
##

data_dir = os.path.join(dire, "shhs_outputs")    
if not os.path.exists(dire):
    os.makedirs(dire, exist_ok=True)
    
shutil.copytree(args.dir, data_dir)

files = os.listdir(data_dir)
files = np.array([os.path.join(data_dir, i) for i in files])
files.sort()


######## pretext files##########

pretext_files = list(np.random.choice(files,264,replace=False))    #change

print("pretext files: ", len(pretext_files))
from tqdm import tqdm


# load files
os.makedirs(dire+"/pretext/",exist_ok=True)

cnt = 0
for file in tqdm(pretext_files):
    x_dat = np.load(file)["x"]*1000
    if x_dat.shape[-1]==2:
        #mean = np.mean(x_dat.reshape(-1,2),axis=0).reshape(1,1,2)
        #std = np.std(x_dat.reshape(-1,2),axis=0).reshape(1,1,2)
        #x_dat = (x_dat-mean)/std
        x_dat = x_dat.transpose(0,2,1)
        x_dat = np.expand_dims(x_dat[:,0,:],1)

        for i in range(half_window,x_dat.shape[0]-half_window):
            dct = {}
            temp_path = os.path.join(dire+"/pretext/",str(cnt)+".npz")
            dct['pos'] = interpolate(torch.tensor(x_dat[i-half_window:i+half_window+1]),scale_factor=3000/3750).numpy()
            #dct['pos'] = x_dat[i-half_window:i+half_window+1]
            np.savez(temp_path,**dct)
            cnt+=1


######## test files##########
test_files = sorted(list(set(files)-set(pretext_files))) 
os.makedirs(dire+"/test/",exist_ok=True)

print("test files: ", len(test_files))

for file in tqdm(test_files):
    new_dat = dict()
    dat = np.load(file)

    if dat['x'].shape[-1]==2:
        
        new_dat['_description'] = [file]
        new_dat['windows'] = interpolate(torch.tensor(dat['x'].transpose(0,2,1)),scale_factor=3000/3750).numpy()*1000
        new_dat['windows'] = np.expand_dims(new_dat['windows'][:,0,:],1)

        new_dat['y'] = dat['y'].astype('int')
        
        temp_path = os.path.join(dire+"/test/",os.path.basename(file))
        np.savez(temp_path,**new_dat)
