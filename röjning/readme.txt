Skript för att hantera röjningsraster

2021: Vegetationskvot och maxhöjd beräknas av TerraScan och exporteras till GeoTiff. 
Beräkning av höjdfaktor och täthetsfaktor, aggregering till större pixlar samt 
beräkning av svårithetsfaktor görs i FME. Klippning med intrångsersatt mark och 
uppdelning i tiles görs också i FME.

2022: Om beräkning av vegetationskvot och maxhöjd kan göras i FME flyttas alla beräkningar
dit. Eventuellt är en förutsättning för att det ska fungera smidigt att vi nu kan arbeta med
1 m-raster som aggregeras till 5 m-raster, eftersom rastercellerna går jämnt upp med 
levererade 500*500 m las-tiles. Om vi som tidigare ska använda 1.5 och 4.5-m raster kommer 
man att behöva läsa in delar av intilliggande tiles men även det bör gå att lösa.
