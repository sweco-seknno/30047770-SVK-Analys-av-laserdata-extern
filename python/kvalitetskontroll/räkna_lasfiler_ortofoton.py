#%%
from pathlib import Path
import pandas as pd

#%%
LGs = ['LG003', 'LG005', 'LG006', 'LG007', 'LG008', 
       'LG011', 'LG012', 'LG013', 'LG014', 'LG015', 
       'LG016', 'LG018', 'LG019', 'LG020', 'LG021', 
       'LG022', 'LG025', 'LG026', 'LG027', 'LG028', 
       'LG029', 'LG031', 'LG032', 'LG034', 'LG035', 
       'LG040', 'LG041', 'LG042', 'LG046', 'LG048', 
       'LG049', 'LG051', 'LG052', 'LG053', 'LG054', 
       'LG055', 'LG056', 'LG057', 'LG058', 'LG066', 
       'LG068', 'LG071', 'LG072', 'LG073', 'LG074', 
       'LG075', 'LG076', 'LG077', 'LG080', 'LG081', 
       'LG082', 'LG084', 'LG086', 'LG087', 'LG088', 
       'LG089', 'LG090', 'LG091', 'LG092', 'LG094', 
       'LG097', 'LG098', 'LG102', 'LG103', 'LG104', 
       'LG106', 'LG107', 'LG108', 'LG109', 'LG110', 
       'LG112', 'LG113', 'LG114', 'LG115', 'LG116', 
       'LG117', 'LG118', 'LG119', 'LG120', 'LG123', 
       'LG126', 'LG129', 'LG132', 'LG133', 'LG134', 
       'LG135', 'LG136', 'LG137', 'LG139', 'LG140', 
       'LG141', 'LG142', 'LG143', 'LG410', 'LG500', 
       'LG555', 'LG661', 'LG700']

datamapp = Path(r"\\sellanas001.sweco.se\26664 Mätdata\Data_SVK\SVK_2023")
txtfil_antal_filer = Path(r"U:\Projekt\Kvalitet\räkna_levererade_filer_2023\räknat_2024-01-17.txt")

#%%
def räkna_filer(LG):
    LG_mapp = datamapp / LG
    tif_filer = list(LG_mapp.rglob("*.tif"))
    las_filer = list(LG_mapp.rglob("*.las"))
    laz_filer = list(LG_mapp.rglob("*.laz"))
    
    return {
        "LG": LG,
        "TIF": len(tif_filer),
        "LAS": len(las_filer),
        "LAZ": len(laz_filer)
    }


# Skapa en lista för varje mapp med antal filer
resultat_lista = [räkna_filer(LG) for LG in LGs]

# Skapa en DataFrame från listan
resultat_df = pd.DataFrame(resultat_lista)

# Spara DataFrame till en textfil
resultat_df.to_csv(txtfil_antal_filer, index=False, sep="\t")

print(f"Resultat har sparats i {txtfil_antal_filer}")

# %%
