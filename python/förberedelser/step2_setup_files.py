# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 12:29:20 2021

@author: SEKNNO
"""
#%% IMPORTER
from pathlib import Path
import pandas as pd
import shutil

#%% VARIABLER
LGs_info = "Ledningar_2024_nya_makron_241112.txt"

analysis_dir = Path(r"Q:\Projekt\Analys_2024")
data_dir = Path(r"Q:\Projekt\Data_2024")
bigdata_dir = Path(r"C:\SVK_2023")
ptc_file = r"Q:\Projekt\Analys_2024\pointclasses.ptc"
macro_dir = analysis_dir / "terrascan_makron"
shellscript_dir = analysis_dir / "shellscript"
dgn_dir = analysis_dir / "DGN"
LGs_info_path = data_dir / "styrfiler" / LGs_info

#%% FUNKTIONER
def create_line_files(row):
    LG = row["LG"]
    line = row["line"]
    spanning = row["Spänning"]
    
    line_dir = analysis_dir / "ledningar" / LG / f"line_{line}"
        
    # create_prj_file(line_dir, LG, line)
    copy_RBX_och_kantträd_macro(line_dir, spanning)
    # copy_DGN(dgn_dir, LG, line)
    # copy_pointdensity_DTM_macro(macro_dir, line_dir)
    # copy_sammanfoga_RBX(shellscript_dir, line_dir)
    
def copy_file(src, dest):
    try:
        shutil.copy(src, dest)
    # e.g. src and dest are the same file
    except shutil.Error as e:
        print(f"Error: {e}")
    # e.g. src or dest doesn't exist
    except IOError as e:
        print(str(dest))
        print(f"Error: e.strerror")
        print("")

def create_prj_file(line_dir, LG, line):
    prj_file = line_dir / f"{LG}_{line}.prj"
    fbi_dir = bigdata_dir / LG / "fbi" / f"{LG}_{line}"
    with open(prj_file, 'w') as f:
        f.write(f"[TerraScan project]\nScanner=Airborne\nStorage=FastBinary\nStoreTime=1\nStoreColor=0\nStoreDistance=0\nStoreGroup=0\nStoreNormal=0\nStoreIntensity=1\nStoreLine=1\nStoreScanner=1\nStoreEcho=1\nStoreAngle=1\nStoreEchoNorm=0\nStoreEchoPos=0\nStoreImage=0\nStoreClass=1\nStoreEchoLen=0\nStoreParam=0\nRequireLock=0\nDescription={LG}_{line}\nFirstPointId=1\nDirectory={str(fbi_dir)}\nPointClasses={str(ptc_file)}\nBlockSize=1000\nBlockGroupCount=1000000\nBlockNaming=0\nBlockPrefix=pt\n")

def copy_RBX_och_kantträd_macro(line_dir, spanning):
    src = macro_dir / f"RBX_och_kantträd_{spanning}_kV.mac"
    dest = line_dir / f"RBX_och_kantträd_{spanning}_kV.mac"
    copy_file(src, dest)

def copy_DGN(dgn_dir, LG, line):
    src = dgn_dir / "MALL.dgn"
    dest = dgn_dir / f"{LG}_{line}.dgn"
    copy_file(src, dest)

def copy_pointdensity_DTM_macro(macro_dir, line_dir):
    src = macro_dir / "DTM_och_antal_sistareturer.mac"
    dest = line_dir / "DTM_och_antal_sistareturer.mac"
    copy_file(src, dest)

def copy_sammanfoga_RBX(shellscript_dir, line_dir):
    src = shellscript_dir / "sammanfoga_RBX-block.bat"
    dest = line_dir / "RBX" / "sammanfoga_RBX-block.bat"
    copy_file(src, dest)
    print("Kopierat sammanfoga RBX")


#%% KÖRNING
# Applicera funktionen create_line_files på alla ledningar i styrfilen (LGs_info_path)
LGs_info = pd.read_csv(LGs_info_path, sep="\t", header=0)
LGs_info.apply(create_line_files, axis=1)



# %%
