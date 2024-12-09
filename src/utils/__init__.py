from .constants import (
    COLNAMES_RATES, COLNAMES_SCALES_BASE, 
    COLNAMES_SCALES_DIFF, COLNAMES_SCALES_FLAT,
    COLNAMES_SCALES_FORMULA, TAX_AUTHORITIES,
    TAXABLE_ENTITIES,TAX_GROUPS
)
from .pipelines import (
    calculate_tax_base,
    clean_rates,
    clean_scales,
    fill_all_taxes,
    fill_taxes,
    retrieve_multipliers,
    retrieve_multipliers_by_year,
    select_scales,
    show_taxes
)
from .scraper import (
    _try_download,
    download_all
)