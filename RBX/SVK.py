# -*- coding: utf-8 -*-
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


#def LG_str(LG):
#    # Returns string LGXXX based on LG number (integer)
#    return(f'LG{str(LG).zfill(3)}')
#
#def get_LG_line_dict(LG_line_voltage_file, LG_col, line_col):
#    from pandas import read_csv
#    df = read_csv(LG_line_voltage_file, sep="\t", header=0)
#    LG_lines = df.groupby(LG_col).agg({line_col : lambda x: x.tolist()})[line_col].to_dict()
#    return(LG_lines)
#
#
#def get_LG_voltage_dict(LG_line_voltage_file, LG_col, voltage_col):
#    from pandas import read_csv
#    df = read_csv(LG_line_voltage_file, sep="\t", header=0)
#    LG_voltages = df.groupby(LG_col).agg({voltage_col : lambda x: x.tolist()})[voltage_col].to_dict()
#    return(LG_voltages)