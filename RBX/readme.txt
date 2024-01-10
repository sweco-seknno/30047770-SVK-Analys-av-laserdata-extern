Skript för bearbetning av RBX-punkter exporterade från TerraScan

2018-2020: RBX-punkter identifierades av TerraScan och exporterades till txt-filer en per block. 
Dessa slogs ihop, konverterades till .shp och importerades tillbaks till TerraScan där falsklarm rensades bort. 
Sedan importerades de rensade punkterna från .dgn-filen till en esri fil-geodatabas.

2021: tidigare metod fungerade inte längre - jag fick inte till att läsa punkter från dgn mha arcpy. 
Det berodde nog på ett fel i min kod (upptäcktes 2022) men eftersom jag inte upptäckte det i tid utan 
trodde att det berodde på microstation eller arcpy gjorde jag en tillfällig lösning: mha FME läsa de rensade 
RBX-punkterna från dgn och spara som shp, för att sedan fortsätta i python.

2022: Eftersom felet i koden är hittat och det fungerar att läsa in punkter från dgn med arcpy gör vi som 
2020 och tidigare: Kör makro, RBX-punkternas X, Y, Z, dZ sparas i en txt-fil per block. Starta windowsterminalen
i mappen där txt-filerna ligger, kör kommando för att slå ihop dem till en enda. Läs in den till dgn-filen.
Granska och eventuellt rensa RBX-punkterna. De rensade punkterna läses sedan in mha arcpy för vidare bearbetning.
