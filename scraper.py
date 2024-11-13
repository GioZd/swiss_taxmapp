from time import sleep
import urllib.request as rq
import json
from icecream import ic

if __name__ == '__main__':
    payload = json.dumps(
        {
            "taxGroup":4,
            "simKey":None,
            "year":2023,
            "taxType":"EINKOMMENSSTEUER"
        }
    )
    req = rq.Request(
        url="https://swisstaxcalculator.estv.admin.ch/delegate/ost-integration/v1/export/tax-scales/EN",
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
    sleep(0.069)
    ic(req.header_items())
    with rq.urlopen(req) as f:
        print(f.headers)
        print(f)
        binary_file = f.read()
        with open('prova.xlsx', 'wb') as output:
            output.write(binary_file)