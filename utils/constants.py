COLNAMES_RATES = [
    'canton_ID', 'canton', 'FSO_ID', 'commune', 
    'income_canton', 'income_commune',
    'income_protestant', 'income_roman', 'income_catholic',
    'assets_canton', 'assets_commune',
    'assets_protestant', 'assets_roman', 'assets_catholic',
    'profit_canton', 'profit_commune', 'profit_church',
    'capital_canton', 'capital_commune', 'capital_church'
]

COLNAMES_SCALES_BASE = [
    'canton_ID', 'canton', 'type_of_tax',
    'taxable_entity', 'tax_authority',
    'taxable_worth', 'additional_percentage',
    'base_amount_CHF'
]

COLNAMES_SCALES_DIFF = [
    'canton_ID', 'canton', 'type_of_tax',
    'taxable_entity', 'tax_authority',
    'to_next_CHF', 'additional_percentage'
]

COLNAMES_SCALES_FLAT = [
    'canton_ID', 'canton', 'type_of_tax',
    'taxable_entity', 'tax_authority', 'tax_rate'
]

COLNAMES_SCALES_FORMULA = [
    'canton_ID', 'canton', 'type_of_tax',
    'taxable_entity', 'tax_authority',
    'taxable_worth', 'formula'
]

TAX_AUTHORITIES = {
    'canton': ['Kanton', 'Canton', 'Cantone'],
    'commune': ['Gemeinde', 'Commune', 'Comune'],
    'federal': ['Bundessteuer', 'Impôt fédéral', 
                'Imposta federale', 'Federal tax']
}

TAXABLE_ENTITIES = {
    'single': [
        'Alleinstehend', 'Alleinstehend ohne Kinder', 
        'Alleinstehend mit / ohne Kinder',
        'Personne vivant seule', 'Personne vivant seule, sans enfant',
        'Personne vivant seule, avec / sans enfant',
        'Persona sola', 'Persona sola senza figli', 'Persona sola con / senza figli',
        'Single', 'Single, no children', 'Single, with / no children' 
    ],
    'with_family': [
        'Verheiratet', 'Verheiratet / Alleinstehend mit Kindern', 
        'Marié(e)', 'Personne mariée / vivant seule, avec enfant',
        'Coniugato', 'Coniugato / persona sola con figli',
        'Married', 'Married/Single, with children',

    ],
    'all': ['Alle', 'Tous', 'Tutti', 'All']
}

TAX_GROUPS = {
    1: 'AG',
    2: 'AI',
    3: 'AR',
    4: 'BE',
    5: 'BL',
    6: 'BS',
    7: 'FR',
    8: 'GE',
    9: 'GL',
    10: 'GR',
    11: 'JU',
    12: 'LU',
    13: 'NE',
    14: 'NW',
    15: 'OW',
    16: 'SG',
    17: 'SH',
    18: 'SO',
    19: 'SZ',
    20: 'TG',
    21: 'TI',
    22: 'UR',
    23: 'VD',
    24: 'VS',
    25: 'ZG',
    26: 'ZH',
    77: 'Conf',
}