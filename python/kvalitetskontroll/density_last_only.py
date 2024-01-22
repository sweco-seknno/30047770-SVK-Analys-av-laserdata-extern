# %% IMPORTER
from pathlib import Path
import numpy as np
import rasterio
from rasterio import mask as msk
from rasterio.crs import CRS
from rasterio.merge import merge
import geopandas as gpd
import pandas as pd

# %% SÖKVÄGAR, VARIABLER
namn_styrfil = "Punkttäthet_YYYY-MM-DD.txt"
buffert_avst = 50 

data_dir = Path(r"\\Seumefs002\projekt\26664\30047770\000\Projekt\Analys_2023\ledningar")
vatten_file = Path(r"U:\Projekt\Data_2023\NMD\vatten_2023_buffrat60\Vatten_mittlinjer60_2023.shp")
LGs_info_path = Path(r"U:\Projekt\Data_2023\styrfiler\punkttäthet") / namn_styrfil
resultat_folder = Path(r"U:\Projekt\Analys_2023\täthetsraster")
resultat_fil = resultat_folder / namn_styrfil


# %% FUNKTIONER
def create_dir(*dirpaths):
    import os
    for dirpath in dirpaths:
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            
def merge_max(old_data, new_data, old_nodata, new_nodata, index=None, roff=None, coff=None):
    old_data[:] = np.maximum(old_data, new_data)  # <== NOTE old_data[:] updates the old data array *in place*

def buffra_mittlinje(LG, line, line_dir, buffert_avst):
    mittlinje_file = line_dir / "mittlinje" / f"{LG}_{line}.shp"
    mittlinje = gpd.read_file(mittlinje_file)
    mittlinje_buffrad_geom = mittlinje.geometry.buffer(buffert_avst, cap_style=2)
    mittlinje_buffrad = gpd.GeoDataFrame(geometry = mittlinje_buffrad_geom)
    return(mittlinje_buffrad)

def öppna_täthetsraster_block(raster_names):
    block_rasters = []
    for raster_name in raster_names:   
        raster = rasterio.open(raster_name, 'r+')
        raster.crs = project_crs
        block_rasters.append(raster)
    return(block_rasters)

def täckningsgrad(klippt_raster):
    #total_nr_pixels = clipped_raster.size
    antal_datapixlar = np.count_nonzero(klippt_raster != -100)
    #no_points = np.count_nonzero(clipped_raster == 0)
    minst_16 = np.count_nonzero(klippt_raster >=400)
    minst_32 = np.count_nonzero(klippt_raster >=800)
    andel_minst_16 = minst_16 / antal_datapixlar
    andel_minst_32 = minst_32 / antal_datapixlar
    return(andel_minst_32, andel_minst_16)

def beräkna_täthet(ledning):
    LG = ledning["LG"]
    line = ledning["line"]   

    line_dir = data_dir / LG / f"line_{line}"
    dst_folder = resultat_folder / LG / f"line_{line}"
    create_dir(dst_folder)

    # vatten = gpd.read_file(vatten_file)
    # project_crs = vatten.crs

    mittlinje_buffrad = buffra_mittlinje(LG, line, line_dir, buffert_avst)
    analysomrade = gpd.overlay(mittlinje_buffrad, vatten, how="difference")

    raster_dir = line_dir / "antal_sistareturer" / "block"
    raster_names = raster_dir.glob("*.tif")
    block_rasters = öppna_täthetsraster_block(raster_names)

    # block_rasters = []
    # for raster_name in raster_names:   
    #     raster = rasterio.open(raster_name, 'r+')
    #     raster.crs = project_crs
    #     block_rasters.append(raster)

    dst_file_unclipped = dst_folder / f"{LG}_{line}_antal_sistareturer_oklippt.tif"
    dst_file_clipped = dst_folder / f"{LG}_{line}_antal_sistareturer.tif"

    mosaic_raster, mosaic_transform = merge(block_rasters, method=merge_max)
    with rasterio.open(dst_file_unclipped, 'w', height=mosaic_raster.shape[1], width=mosaic_raster.shape[2], count=mosaic_raster.shape[0], dtype=mosaic_raster.dtype, crs=project_crs, transform=mosaic_transform) as dst:
        dst.write(mosaic_raster)

    with rasterio.open(dst_file_unclipped, 'r+') as raster:
        raster.crs = project_crs
        clipped_raster, clipped_transform = msk.mask(raster, analysomrade.geometry, crop=True, nodata=-100)

        with rasterio.open(dst_file_clipped, 'w', height=clipped_raster.shape[1], width=clipped_raster.shape[2], count=clipped_raster.shape[0], dtype=clipped_raster.dtype, crs=project_crs, transform=clipped_transform) as dst:
            dst.write(clipped_raster)

    # total_nr_pixels = clipped_raster.size
    # nr_data_pixels = np.count_nonzero(clipped_raster != -100)
    # no_points = np.count_nonzero(clipped_raster == 0)
    # at_least_16 = np.count_nonzero(clipped_raster >=400)
    # at_least_32 = np.count_nonzero(clipped_raster >=800)

    # ratio_at_least_16 = at_least_16 / nr_data_pixels
    # ratio_at_least_32 = at_least_32 / nr_data_pixels
    andel_minst_32, andel_minst_16 = täckningsgrad(clipped_raster)

    with open(resultat_fil, 'a') as fil:
        fil.write(f"{LG}\t{line}\t{andel_minst_32}\t{andel_minst_16}\n")

    # black = np.count_nonzero(clipped_raster == 0)
    # red = np.count_nonzero((clipped_raster >=0) & (clipped_raster<=399))
    # yellow = np.count_nonzero((clipped_raster >=400) & (clipped_raster<=799))
    # green = np.count_nonzero((clipped_raster >=800) & (clipped_raster<=1599))
    # blue = np.count_nonzero(clipped_raster >=1600)

    # print()
    # print(f"{LG}_line{line}:")
    # print(f"{black} {red} {yellow} {green} {blue}")

    # nrTot = black + red + yellow + green + blue
    # nrGT800 = green + blue
    # nrGT400 = yellow + green + blue

    # andel_GT400 = nrGT400 / nrTot
    # andel_GT800 = nrGT800 / nrTot

    # print(f"andel>32: {andel_GT800}, andel>16: {andel_GT400}")
    # print((nrTot+nodata - clipped_raster.shape[1]*clipped_raster.shape[2])/(nrTot+nodata))
    
    print(f"{LG}\t{line}\t{andel_minst_32}\t{andel_minst_16}")

# %% KÖRNING
vatten = gpd.read_file(vatten_file)
project_crs = vatten.crs

with open(resultat_fil, 'w') as fil:
        fil.write(f"LG\tledning\t>=32 pt/m2\t>=16 pt/m2\n")
    
LGs_info = pd.read_csv(LGs_info_path, sep="\t", header=0)
LGs_info.apply(beräkna_täthet, axis=1)

# %%
