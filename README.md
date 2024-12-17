![README Taxmapp](elements/taxmapp.svg)
# README
## TAXMAPP - The Ultimate Swiss Taxes Comparator
Switzerland has been a federal republic since 1848, hence its own cantons may differ significantly in regulations, permissions, prohibitions and... taxes!
This app can offer you a preview of what could be the most convenient places where to settle down in the Helvetic territory, based on a tax comparison between cantons and municipalities.

[!NOTE]: This tool offers only approximate calculations that ignore important features and articulations of official tax computations, that take into consideration also religion, age, familiar status and so on.

## Getting started
Download the official [GitHub repository](https://github.com/GioZd/swiss_taxmapp) through HTTPS with the command line
> git clone https://github.com/GioZd/swiss_taxmapp.git
or through SSH protocol with the command line
> git clone git@github.com:GioZd/swiss_taxmapp.git
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
that will instantiate and activate a virtual environment containing all correct dependencies, including Python 3.13.


Ci sono sostanzialmente tre tipi di tassazione:
1. (base + differenza) * % dello scaglione (es. Ticino)
2. sum(delta_i * %_i) (es. Argovia)
3. flat tax <math>\sum x_i</math>

Alla categoria 1. appartengono:
- BS
- Confederazione
- FR
- GE
- GL
- GR
- NE
- SH
- SO
- TG
- TI
- VD
- VS
- ZG

Alla categoria 2. appartengono:
- AG
- AI
- AR
- BE
- JU
- LU
- NW
- SG
- SZ
- ZH

Alla categoria 3. appartengono:
- OW
- UR

Infine c'è Basilea (BL) con dei problemi mentali, cioè c'è una formula.

N.B.: tra sostanza e reddito possono esserci variazioni di presentazione
o di formulazione. L'elenco puntato si riferisce alla tassa sul reddito.

## Enhancement proposals
1. More accurate tax calculations:
    - computation of personal tax,
    - computation of church tax,
    - using spil factor for couples,
    - computation of various deductions (presence of children, celibacy, young age etc.).
2. Interactive maps: due to Streamlit limitations an interaction with the mouse cursor has not been possible, but other libraries such as <tt>pydeck</tt> might be more compatible with Streamlit.
3. Selection by travel distance (multiple data sources can be found on the Internet under Open License).
4. Progressively populating SQLite database to collect increasingly more data without overwriting the previous.
5. Code optimization for faster response and visualization.
6. Translations to French or other languages.

## Stable version
v.1.1.2

## Credits