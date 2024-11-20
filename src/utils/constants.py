COLNAMES_RATES = [
    'canton_ID', 'canton', 'FSO_ID', 'commune', 
    'income_canton', 'income_commune',
    'income_protestant', 'income_roman', 'income_catholic',
    'assets_canton', 'assets_commune',
    'assets_protestant', 'assets_roman', 'assets_catholic',
    'profit_canton', 'profit_commune', 'profit_church',
    'capital_canton', 'capital_commune', 'capital_church'
]

COLNAMES_SCALES = [
    'canton_ID', 'canton', 'type_of_tax',
    'taxable_entity', 'tax_authority',
    'taxable_worth', 'additional_percentage',
    'base_amount_CHF'
]

TAXABLE_ENTITIES = {
    'single': [
        'Alleinstehend ohne Kinder',
        'Personne vivant seule, sans enfant',
        'Persona sola senza figli',
        'Single, no children'
    ],
    'with_family': [
        'Verheiratet / Alleinstehend mit Kindern',
        'Personne mariée / vivant seule, avec enfant',
        'Coniugato / persona sola con figli',
        'Married/Single, with children'
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