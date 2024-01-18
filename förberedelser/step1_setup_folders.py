# -*- coding: utf-8 -*-
"""
Created on Fri Aug 27 16:56:11 2021

@author: SEKNNO
"""

#%% IMPORTER
from pathlib import Path
import pandas as pd

#%% VARIABLER
prj_dir = Path(r"U:\Projekt\Analys_2023\ledningar")
LGs_info_path = r"U:\Projekt\Data_2023\styrfiler\Ledningar_2023.txt"

#%% FUNKTIONER
def create_dir(*dirpaths):
    import os
    for dirpath in dirpaths:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            print(f"{dirpath}  created.")
        else:
            print(f"{dirpath}  already exists. Not overwritten.")

def create_line_directories(row):
    LG = row["LG"]
    line = row["line"]
    
    # Sökvägar och namn på mappar som ska skapas    
    line_dir = prj_dir / LG / f"line_{line}"   
    mittlinje_dir = line_dir / "mittlinje"

    RBX_dir = line_dir / "RBX" / "block"
    kanttrad_dir = line_dir / "kantträd" / "block"
    ROJ_dir = line_dir / "röjning" / "block"

    höga_föremål_dir = line_dir / "höga_föremål" / "block"
    RBX_akuta_dir = line_dir / "RBX_akuta" / "block"

    antal_sistareturer_dir = line_dir / "antal_sistareturer" / "block"
    DTM_dir = line_dir / "DTM" / "block"
    
    # Skapa mapparna
    create_dir(line_dir, mittlinje_dir)
    create_dir(RBX_dir, kanttrad_dir, ROJ_dir)
    create_dir(höga_föremål_dir, RBX_akuta_dir)
    create_dir(antal_sistareturer_dir, DTM_dir)
   
#%% KÖRNING
# Applicera funktionen create_line_directories på 
# varje ledning i styrilen (LGs_info_path):   
LGs_info = pd.read_csv(LGs_info_path, sep="\t", header=0)
LGs_info.apply(create_line_directories, axis=1)
