Skript för bearbetning av RBX-punkter exporterade från TerraScan


2022: Kör makro, RBX-punkternas X, Y, Z, dZ sparas i en txt-fil per block. Starta windowsterminalen
i mappen där txt-filerna ligger, kör kommando för att slå ihop dem till en enda. Läs in den till dgn-filen.
Granska och eventuellt rensa RBX-punkterna. De rensade punkterna i dgn-filen läses sedan in mha arcpy för vidare bearbetning. 
Txt-filen med alla punkter används för att få med höjd över mark.

TODO: Vimaps data från 2022 och 2023 har varit av så hög kvalitet att vi inte har behövt rensa några falsklarm. Då är
inläsningen till DGN-filen onödig och lätt att glömma. Ändra i skriptet så att endast punkter från txt-filen läses in.
Spara ändå skript med den gamla metoden ifall vi i framtiden får sämre data med falsklarm som behöver rensas bort