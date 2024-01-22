# -*- coding: utf-8 -*-
# TODO: kolla vilka skript/notebooks som använder dessa funktioner. 
# Se även över SKB.py i samma veva - lägg alla funktioner i samma fil?

"""
Created on Fri Aug 27 16:13:35 2021

@author: SEKNNO
"""

from pathlib import Path
import shutil
import fileinput
import os
import glob


def create_dir(*dirpaths):
    import os
    for dirpath in dirpaths:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            print(f"{dirpath}  created.")
        else:
            print(f"{dirpath}  already exists. Not overwritten.")


def copy_file(src, dest):
    try:
        shutil.copy(src, dest)
    # e.g. src and dest are the same file
    except shutil.Error as e:
        print(f"Error: {e}")
    # e.g. src or dest doesn't exist
    except IOError as e:
        print(f"Error: e.strerror")


def merge_shapefiles(infiles):
    import geopandas as gpd
    import pandas as pd
    indata = [gpd.read_file(infile) for infile in infiles]
    indata_combined = gpd.GeoDataFrame(pd.concat(indata, ignore_index=True), crs=indata[0].crs)
    return(indata_combined)


def merge_blocks(src_dir, search_pattern, dst_file):
    blocks = glob.glob(os.path.join(src_dir, search_pattern))
    with open(dst_file, "w") as fh:
        input_lines = fileinput.input(blocks)
        fh.writelines(input_lines)
        

def replace_line_in_file(infile, newfile, oldLine, newLine):
    with open(infile, 'r') as input_file, open(newfile, 'w') as output_file:
        for line in input_file:
            if line.strip() == oldLine:
                output_file.write(f"{newLine}\n")
            else:
                output_file.write(line)

