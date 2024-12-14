![README Taxmapp](elements/taxmapp.png.jpg)
# README
Ci sono sostanzialmente tre tipi di tassazione:
1. (base + differenza) * % dello scaglione (es. Ticino)
2. sum(delta_i * %_i) (es. Argovia)
3. flat tax

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