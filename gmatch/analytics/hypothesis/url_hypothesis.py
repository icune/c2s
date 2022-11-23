"""Check if any part of name contained in company url."""
import csv
import re
from collections import Counter
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from gmatch.analytics.load_data import load_data
from gmatch.gmatch.items import GoogleItem


def match_name_with_url(name: str, url: str, stop_domains: List[str]) -> bool:
    if not url:
        return False

    if any([sw in url for sw in stop_domains]):
        return False

    stop_words = ['inc', 'llc', 'company']
    rem_symbols = r'\.|,'

    parts = re.split(r'\s+', name)
    parts = [p.lower() for p in parts]
    parts = [re.sub(rem_symbols, '', p) for p in parts]
    parts = [p for p in parts if p not in stop_words]

    url_domain = urlparse(url).netloc

    return any([(p in url_domain) for p in parts])


def domain_2l(domain: str) -> str:
    return '.'.join(domain.split('.')[-2:])


def find_stop_domains(data: List[GoogleItem]) -> List[str]:

    domain_counter = Counter(sum([
        [
            domain_2l(urlparse(sl.href).netloc) for sl in gi.search_list if sl.href
        ]
        for gi in data
    ], []))

    return [d for d, c in domain_counter.items() if c > 1]


if __name__ == "__main__":
    data = load_data()

    stop_domains = find_stop_domains(data)

    data_folder = Path(__file__).parent / "data"

    with open(data_folder / "stop_domains.txt", "r") as f:
        manual = [l.strip() for l in f.read().split("\n") if l]
        stop_domains.extend(manual)

    ret = {}
    for row in data:
        ret[row.company.name] = None
        for sl in row.search_list:
            if match_name_with_url(row.company.name, sl.href, stop_domains):
                ret[row.company.name] = sl.href
                break

    result_rows = [["Company", "Address", "Site"]]

    for row in data:
        result_rows.append([
            row.company.name,
            row.company.address,
            ret[row.company.name]
        ])

    with open(data_folder / 'result.csv', 'w') as file:
        writer = csv.writer(file)
        for row in result_rows:
            writer.writerow(row)





