# %% IMPORTERA PAKET
from pathlib import Path
import pylas
import pandas as pd
import datetime

# %% VARIABLER OCH SÖKVÄGAR
prj_dir = Path(r"C:\SVK_2023\skanningsdatum")
LG= ['LG011', 'LG011', 'LG012', 'LG012', 'LG012', 
	 'LG019', 'LG019', 'LG019', 'LG019', 'LG019', 
	 'LG019', 'LG020', 'LG020', 'LG021', 'LG022', 
	 'LG022', 'LG032', 'LG032', 'LG032', 'LG032', 
	 'LG032', 'LG032', 'LG032', 'LG032', 'LG032', 
	 'LG032', 'LG035', 'LG046', 'LG046', 'LG046', 
	 'LG046', 'LG046', 'LG046', 'LG046', 'LG053', 
	 'LG053', 'LG053', 'LG053', 'LG054', 'LG055', 
	 'LG055', 'LG056', 'LG058', 'LG081', 'LG081', 
	 'LG082', 'LG082', 'LG082', 'LG082', 'LG084', 
	 'LG086', 'LG087', 'LG087', 'LG087', 'LG087', 
	 'LG087', 'LG087', 'LG087', 'LG087', 'LG088', 
	 'LG088', 'LG088', 'LG088', 'LG088', 'LG088', 
	 'LG088', 'LG088', 'LG088', 'LG089', 'LG090', 
	 'LG094', 'LG094', 'LG094', 'LG094', 'LG094', 
	 'LG098', 'LG098', 'LG102', 'LG102', 'LG102', 
	 'LG129', 'LG132', 'LG132', 'LG132', 'LG132', 
	 'LG133', 'LG135', 'LG135', 'LG141', 'LG141', 
	 'LG141', 'LG142', 'LG700', 'LG700']

skanningsdatum_fil = prj_dir / "skanningsdatum_alla.txt"

data_dir = Path(r"\\sellanas001.sweco.se\26664 Mätdata\Data_SVK\SVK_2023")
laslista_fil = prj_dir / "tile_mitt_på_ledningen.txt"

filtyper = [".las", ".laz"]
epoch_start = datetime.datetime(1980, 1, 6)

# %% LÄS IN DATA
laslista_alla = pd.read_csv(laslista_fil, sep="\t", names=["PageName", "LG_value", "line"])
laslista = laslista_alla[laslista_alla['LG_value'].isin(LG)]
resultat_data = []

# %% FUNKTIONER
def hitta_fil(mapp_path, filnamn, filtyper):
    # Loopa igenom alla filer i mappen och dess undermappar
    for fil_path in mapp_path.rglob('*'):
        if fil_path.stem == filnamn and fil_path.suffix in filtyper:
            # Om filen matchar både namnet och en av de angivna ändelserna, skriv ut sökvägen
            return(fil_path)

# %% HUVUDLOOP
for index, row in laslista.iterrows():
    PageName = row["PageName"]
    LG_value = row["LG_value"]
    line = row["line"]
    skanningsdatum_formaterat = ""  # Standardvärde

    filnamn = f"{LG_value}_{PageName}"
    las_dir = data_dir / LG_value

    las_fil = hitta_fil(las_dir, filnamn, filtyper)


    try:
        las = pylas.read(str(las_fil))
        punkt = las[0]
        gps_tid = punkt["gps_time"]
        skanningstidpunkt = epoch_start + datetime.timedelta(seconds=gps_tid)
        skanningsdatum_formaterat = skanningstidpunkt.strftime("%Y-%m-%d")
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Ett fel uppstod: {str(e)}")
    
    resultat_data.append([PageName, LG_value, line, skanningsdatum_formaterat])

resultat = pd.DataFrame(resultat_data, columns=["PageName", "LG_value", "line", "skanningsdatum"])

resultat.to_csv(skanningsdatum_fil, sep="\t", index=False)
# %%
