![README Taxmapp](elements/taxmapp.svg)
# README
## TAXMAPP - The Ultimate Swiss Taxes Comparator
Switzerland has been a federal republic since 1848, hence its own cantons may differ significantly in regulations, permissions, prohibitions and... taxes!
This app can offer you a preview of what could be the most convenient places where to settle down in the Helvetic territory, based on a tax comparison between cantons and municipalities.

## Getting started
Download the official [GitHub repository](https://github.com/GioZd/swiss_taxmapp) through HTTPS with the command line
```sh
git clone https://github.com/GioZd/swiss_taxmapp.git
```

or through SSH protocol with the command line
```sh
git clone git@github.com:GioZd/swiss_taxmapp.git
```

If having any troubles or not having Git installed, just download and decompress the zip folder.

Before launching the program, Python 3 and packages `streamlit`, `polars`, `altair`, `geopandas` and `xlsx2csv` must be installed (working versions for Python and for each dependency are pinned in the `pyproject.toml`).
To launch the program, execute the following command from the project folder:
```sh
streamlit run app.py
```
If using `uv` software as environment manager run preferably
```sh
uv run streamlit run app.py
```
that will instantiate and activate a virtual environment containing all correct dependencies, including Python 3.13.[[1](#1)]

## About Swiss cantons
Switzerland is a Federal Republic divided into 26 cantons. For convenience the names of the cantons are mostly abbreviated with their official codes throughout the app and hereafter in the README.[[2](#2)]

| Code | Name | Capital |
| ---- | ---- | ------- |
| ZH | Zurich | Zurich |
| BE | Bern | Bern |
| LU | Lucerne | Lucerne |
| UR | Uri | Altdorf |
| SZ | Schwyz | Schwyz |
| OW | Obwalden | Sarnen |
| NW | Nidwalden | Stans |
| GL | Glarus | Glarus |
| ZG | Zug | Zug |
| FR | Freiburg | Freiburg |
| SO | Solothurn | Solothurn |
| BS | Basel-Stadt | Basel |
| BL | Basel-Landschaft | Liestal |
| SH | Schaffhausen | Schaffhausen |
| AR | Appenzell Ausserrhoden | Herisau |
| AI | Appenzell Innerrhoden | Appenzell |
| SG | St. Gallen | St. Gallen |
| GR | Graubünden | Chur |
| AG | Aargau | Aarau |
| TG | Thurgau | Frauenfeld |
| TI | Ticino | Bellinzona |
| VD | Vaud | Lausanne |
| VS | Valais | Sion |
| NE | Neuchâtel | Neuchâtel |
| GE | Geneva | Geneva |
| JU | Jura | Delémont | 


## Insights of data collection and tax calculation

Data were collected from this [online tool](https://swisstaxcalculator.estv.admin.ch/) for tax calculation supplied by the Federal Tax Administration, in the form of Excel tables.
The data show 4 different main patterns, briefly described below.
1. $\Delta_s\times c_s\% + \text{Tax Base}$ where $\Delta_s=\text{Value}-\text{Floor Rank(Value)}$ and $c_s\%$ is a rank-relative coefficient. Income tax for BS, FR, GE, GL, GR, LU, NE, SH, SO, TG, TI, VD, VS, ZG, assets tax for AR, BE, BL, BS, FR, GE, JU, NE, SO, TI, VD, VS, ZG and the Federal Tax follow this formula. Eg. in canton Geneva (GE) a CHF 100,000 income implies a $(100,000-76,812)\times 15.5\% +7,828=\text{CHF } 11,422.14$ base for further numeric processing. Tax base may be fixed by the canton or calculated iteratively starting form zero.
2. $\sum_{i=1}^{s}\Delta_i\cdot c_i\%$ that means that a CHF 100,000 income in Zurich will be divided as follows: $(6,900\times 0\%) + (4,900\times 2\%) + \dots + (17,400\times 8\%) + (\text{remaining }24,600\times 9\%)=\text{CHF }6,207$ (then further processed). Income tax for AG, AI, AR, BE, BL, JU, NW, SG, SZ, ZH and assets tax for AG, GR, SH and ZH follow this procedure.
3. Flat tax, a unique rate factor for boundless wealth, such as income tax in OW and UR and assets tax in AI, GL, LU, NW, OW, SG, SZ, TG and UR.
4. BL (Basel-Landschaft) pursues its own way, namely a rank-based formula. Assuming to be in the $s$-th wealth rank, the formula looks like $a_s\cdot \mathrm{Value}+b_s\cdot\mathrm{Value}\cdot\left(\log(\mathrm{Value}) - 1\right)+c_s$.
Then this values are multiplied for a specific factor depending on the canton and the commune and finally summed together.

DISCLAIMER: This app offers only approximate calculations that ignore important features and articulations of official tax computations, that take into consideration also religion, age, familiar status and so on. Furthermore, even the online tool for tax calculation supplied by the Federal Tax Administration (source of all data) claims not to be binding.[[3](#3)] [[4](#4)]

## Geographical data

Geographical datasets to draw the base map in the homepage section are released periodically by the Federal Statistical Office under [OPEN-BY-ASK](https://www.bfs.admin.ch/bfs/en/home/bfs/bundesamt-statistik/nutzungsbedingungen.html) License.[[5](#5)] Coordinates are expressed by default in the CH1903+ (LV95) coordinate reference system, by which positions are measured in meters North/South-ward and East/West-ward from the old observatory of Bern, plus two different constants (one for the North direction, one for the South). Geopandas GeoDataFrame offers a method to trace back to the more familiar EPSG:4326 coordinate reference system and then project the map with the most common projection types (Mercator by Altair default). Alternatively, this dataframe has a structure that allows to be projected as-is, with type of projection equal to "identity". This approach mantains the Swiss predefined "Swiss-grid" projection, a cylindrical projection centered in Bern.[[6](#6)] However, the former method was preferred, beacuse it doesn't affect significantly the comparison between internal surfaces, due to Switzerland's small sizes and it is more understandable.


## Enhancement proposals
1. More accurate tax calculations:
    - computation of personal tax,
    - computation of church tax,
    - using spil factor for couples,
    - computation of various deductions (presence of children, celibacy, young age etc.).
2. Interactive maps: due to Streamlit limitations an interaction with the mouse cursor has not been possible, but other libraries such as `pydeck` might be more compatible with Streamlit.
3. Selection by travel distance (multiple data sources can be found on the Internet under Open License).
4. Progressively populating SQLite database to collect increasingly more data without overwriting the previous.
5. Code optimization for faster response and visualization.
6. Translations to German, Italian, French or other languages.

## Stable version
v.1.1.2

## References and data sources
[<a id="1"></a>1] uv. Astral Docs. [https://docs.astral.sh/uv](https://docs.astral.sh/uv). An extremely fast Python package and project manager, written in Rust.

[<a id="2"></a>2] Cantons of Switzerland - Wikipedia. [https://en.wikipedia.org/wiki/Cantons_of_Switzerland](https://en.wikipedia.org/wiki/Cantons_of_Switzerland)

[<a id="3"></a>3] FTA Tax Calculator. Accessed December 18, 2024. [https://swisstaxcalculator.estv.admin.ch](https://swisstaxcalculator.estv.admin.ch/#/home). Data source and documentation.

[<a id="4"></a>4] Federal tax administration FTA. [https://www.estv.admin.ch/estv/en/home.html](https://www.estv.admin.ch/estv/en/home.html). FTA website for more detailed readings.

[<a id="5"></a>5] Base Maps - Federal Statistical Office FSO. [https://www.bfs.admin.ch/bfs/en/home/statistics/regional-statistics/base-maps.html](https://www.bfs.admin.ch/bfs/en/home/statistics/regional-statistics/base-maps.html). Geographical databases for statistical mapping.

[<a id="6"></a>6] Geodetic Reference systems - Federal Office of Topography (swisstopo). [https://www.swisstopo.admin.ch/en/geodetic-reference-systems](https://www.swisstopo.admin.ch/en/geodetic-reference-systems). Deeper information about the Swiss reference system.

## License and Credits
The code is under [MIT License](LICENSE).

Data hereby provided are under their respective licenses and ownerships.

---
Giovanni Zedda, BSc student at the Department of Statistical Sciences

University of Padua, 19 December 2024

---
Copyright (c) 2024 Giovanni Zedda