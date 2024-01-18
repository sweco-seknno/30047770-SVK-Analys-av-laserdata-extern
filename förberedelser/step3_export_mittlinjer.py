# -*- coding: utf-8 -*-
"""
Created on Fri Sep 17 16:02:59 2021

@author: SEKNNO
"""

# Mittlinjer till rätt mapp LGXXX / line_y

#%%
import geopandas as gpd
from pathlib import Path
import os

#%%
prj_dir = Path(r"U:\Projekt")
mittlinjer_shp = prj_dir / "Data_2023" / "mittlinjer" / "mittlinjer_2023.shp"

mittlinjer = gpd.read_file(mittlinjer_shp)

#%%
for i in mittlinjer.index:
    mittlinje = mittlinjer.iloc[[i]]
    LG = mittlinje.iloc[0]["LG_value"]
    line = str(int(mittlinje.iloc[0]["line"]))
    mittlinje_shp = prj_dir / "Analys_2023" / "ledningar" / LG / f"line_{line}" / "mittlinje" / f"{LG}_{line}.shp"
    mittlinje.to_file(str(mittlinje_shp))
    print(mittlinje_shp)
