# %%
from pathlib import Path
import geopandas as gpd

# %%
lokal_dir = Path(r"C:\SVK_2023")
prj_dir = Path(r"U:\Projekt")

tile_fil = prj_dir / "Data_2023" / "Underlag_SVK" / "ExSKN23" / "Grd23.shp"
mittlinjer_fil = prj_dir / "Data_2023" / "mittlinjer" / "mittlinjer_2023.shp"

# %%
tiles = gpd.read_file(tile_fil)
mittlinjer = gpd.read_file(mittlinjer_fil)

mittpunkter = mittlinjer.copy()
mittpunkter["geometry"] = mittlinjer.geometry.interpolate(0.5, normalized=True)
mittpunkter.crs = tiles.crs
# %%
join = gpd.sjoin(tiles, mittpunkter, predicate="contains")
join['line'] = join['line'].round().astype(int)
resultat = join[["PageName", "LG_value", "line"]]

# %%
resultat.to_csv(lokal_dir / "skanningsdatum" / "tile_mitt_på_ledningen.txt", sep="\t", index=False)




# %%
