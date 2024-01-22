Skript för bearbetning av kantträdsdata från TerraScan

Namnet SKB kommer från att Svenska kraftnäts benämning Skoglig besiktning, vilket är vad de gör
när de letar kantträd. Överväg att byta namn till något mer begripligt.

I TerraScan har kantträd identifierats: vegetationsreturer grupperas med TerraScans "tree logic". 
Högsta punkten i varje trädgrupp klassas som trädtopp. Trädtoppar som vid fall kan nå inom ett 
angivet säkerhetsavstånd från faslina exporteras till txt-filer, en per block. txt-filen innehåller
X, Y, Z och dZ för varje sådan trädtopp. X, Y, Z är toppens koordinater i Sweref99 TM / RH2000, dZ
är trädtoppens höjd över mark.

I python görs sedan följande (mycket kortfattat):
Avstånd mellan trädets groningspunkt (marken under toppen) och faslina beräknas mha arcpy Near3D. Vi 
kan kalla det avståndet för avst_mark
Trädtoppens minsta avstånd till fas beräknas som avst_mark - dZ (dZ är trädets höjd)
Trädets horisontella avstånd till fas beräknas mha arcpy Near
(Near3D ger också ett horisontellt avstånd, men inte kortaste vägen i horisontell led utan
till den punkt dit 3D-avståndet är kortast, vilket inte behöver vara vinkelrät mot ledningen beroende
på dess nedhäng)

Kantträden delas upp i akuta och ej akuta, där akuta är de träd som har <1 m avstånd till fas vid fall.
Oklart om vi ska göra den uppdelningen i år.

SKB.ipynb: jupyter notebook, utgå från denna
SKB.py: olika funktioner som har med kantträden att göra. Anropas från SKB.ipynb
