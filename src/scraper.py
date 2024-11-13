import json
import os
import sys
import urllib.request as rq

from urllib.error import HTTPError
from time import sleep
from datetime import datetime

from utils import TAX_GROUPS

API_URLS = {
    'rates': (
        "https://swisstaxcalculator.estv.admin.ch"
        "/delegate/ost-integration/v1/export/income-tax-scales/{}"
    ),
    'scales': (
        "https://swisstaxcalculator.estv.admin.ch"
        "/delegate/ost-integration/v1/export/tax-scales/{}"
    )
}
TAX_TYPES = {
    'assets': 'VERMOEGENSSTEUER',
    'income': 'EINKOMMENSSTEUER' 
}

def _try_download(taxGroup: int, year: int, 
                  taxType: str | None = None, 
                  rs: str = 'rates', lang: str = 'EN') -> None:
    sleep(0.1)
    if taxType.lower() not in ['income', 'assets'] and rs == 'scales':
        raise ValueError('`type_of_tax` should be either "income" or "assets"')
    
    payload = json.dumps(
        {
            "taxGroup": 99 if rs == 'rates' else taxGroup,
            "simKey": None,
            "year": year,
            "taxType": None if rs == 'rates' else TAX_TYPES[taxType]
        }
    )
    req = rq.Request(
        url = API_URLS[rs].format(lang.upper()),
        headers = {
            "User-Agent":  ' '.join([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "AppleWebKit/537.36 (KHTML, like Gecko)", 
                "Chrome/130.0.0.0",
                "Safari/537.36", 
                "Edg/130.0.0.0"
            ]),
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": (
                "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,"
                "de-AT;q=0.6,de;q=0.5,en-GB;q=0.4"
            ),
             "content-type": "application/json" 
        },
        data = payload.encode()
    )
    with rq.urlopen(req) as f:
        binary_file = f.read()
        filepath = f'./data'
        if rs == 'rates':
            filepath += f'/rates/estv_rates_{year}.xlsx'
        else:
            filepath += f'/scales/{taxType}/{year}' 
            filepath += f'/estv_scales_{TAX_GROUPS[taxGroup]}.xlsx' 
        if not os.path.isdir('/'.join(filepath.split('/')[:-1])):
            os.makedirs('/'.join(filepath.split('/')[:-1]))
        with open(filepath, 'wb') as output:
            output.write(binary_file)


def download_all(year: int = datetime.today().year, 
            taxType: str | None = None, 
            rs: str = 'rates', lang: str = 'EN') -> None:
    for key in TAX_GROUPS.keys():
        try:
            _try_download(key, year, taxType, rs, lang)
        except HTTPError as e:
            print(e)

if __name__ == '__main__':
    download_all(taxType='income', rs='scales')
    download_all(taxType='assets', rs='scales')