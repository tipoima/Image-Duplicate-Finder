import os
from PIL import Image,ImageFile,UnidentifiedImageError
import pandas as pd
import numpy as np
from PHash import PHash
from multiprocessing import Pool,freeze_support
from functools import partial
from xxhash import xxh32

ImageFile.LOAD_TRUNCATED_IMAGES = True

def xhash(data):
    return xxh32(data).intdigest()

def parallelize(data, func, num_of_processes=8): #tnx https://stackoverflow.com/questions/26784164/pandas-multiprocessing-apply
    num_of_processes=min(np.shape(data)[0],num_of_processes)    
    data_split = np.array_split(data, num_of_processes)
    with Pool(num_of_processes) as pool:
        data = pd.concat(pool.map(func, data_split))
        pool.close()
        pool.join()
    return data
def run_on_subset(func, data_subset):
        
    return data_subset.apply(func, axis=1)

def parallelize_on_rows(data, func, num_of_processes=8):
    return parallelize(data, partial(run_on_subset, func), num_of_processes)

def callGrayscaleHash(row):
    if pd.isna(row['gsHash']):
        try:
            with Image.open(row['path']) as img:
                return str(PHash.grayscaleHash(img))
        except FileNotFoundError:
            return 0|1<<PHash.HASH_LENGTH
    else:
        return row['gsHash']
    
def callRGBHash(row):
    if pd.isna(row['rgbHash']): 
        try:
            with Image.open(row['path']) as img:
                return str(PHash.RGBHash(img))
        except FileNotFoundError:
            return 0|1<<PHash.HASH_LENGTH*3
    else:
        return row['rgbHash']


class ImageCollector:
    
    def getImages(folder:str,useRGB=False,useThreading=True):
        
        scannedImages=ImageCollector.__buildDataFrame(folder)
        
        if useRGB:
            if useThreading:
                scannedImages['rgbHash']=parallelize_on_rows(scannedImages, callRGBHash)
            else:
                scannedImages['rgbHash']=scannedImages.apply(callRGBHash,axis=1)        
        else:
            if useThreading:
                scannedImages['gsHash']=parallelize_on_rows(scannedImages, callGrayscaleHash)
            else:
                scannedImages['gsHash']=scannedImages.apply(callGrayscaleHash,axis=1)

        dirHash=xhash(folder)
        if not os.path.exists("precomputedDirectories"):
            os.mkdir("precomputedDirectories")
        scannedImages.to_pickle(f"precomputedDirectories\\{dirHash}.pkl")
        
        return scannedImages
        
        
    def __buildDataFrame(folder:str):
        _,scannedImages=ImageCollector.__getPaths(folder)
        
        scannedImages=pd.DataFrame(scannedImages,columns=["path","gsHash","rgbHash"])
        scannedImages.index=scannedImages['path']
        dirHash=xhash(folder)
        if os.path.isfile(f"precomputedDirectories\\{dirHash}.pkl"):
            try:
                oldDataFrame=pd.read_pickle(f"precomputedDirectories\\{dirHash}.pkl")
                scannedImages=scannedImages.fillna(oldDataFrame)
            except:
                pass
        return scannedImages
        

    def __getPaths(folder:str): #tnx https://stackoverflow.com/questions/18394147/how-to-do-a-recursive-sub-folder-search-and-return-files-in-a-list
        
        subfolders, files = [], []
        
        for f in os.scandir(folder):
            if f.is_dir():
                subfolders.append(f.path)
            if f.is_file():
                try:
                    with Image.open(f.path):
                        pass
                except UnidentifiedImageError:
                    continue
                files.append((f.path,None,None))
    
        for folder in list(subfolders):
            sf, f = ImageCollector.__getPaths(folder)
            subfolders.extend(sf)
            files.extend(f)
        return subfolders,files
    
if __name__ == "__main__":
    freeze_support()    
    
    

