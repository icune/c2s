"""Module with hypotheses."""
import csv
import re
from pathlib import Path
from typing import List, Callable
from urllib.parse import urlparse

from gmatch.gmatch.items import GoogleItem, GoogleSearchListItem, CompanyInitialInfo

DATA_FOLDER = Path(__file__).parent / "data"


def get_manual_stop_domains() -> List[str]:
    with open(DATA_FOLDER / "stop_domains.txt", "r") as f:
        return [l.strip() for l in f.read().split("\n") if l.strip()]


def get_company_stop_words() -> List[str]:
    with open(DATA_FOLDER / "company_stop_words.txt", "r") as f:
        return [l.strip() for l in f.read().split("\n") if l.strip()]


def write_result_csv(rows: List[List[str]], file_name: str = None) -> None:
    if not file_name:
        raise Exception("Specify file name")
    with open(DATA_FOLDER / file_name, 'w') as file:
        writer = csv.writer(file)
        for row in rows:
            writer.writerow(row)


def lemmatize_company(name: str, stop_words: List[str]) -> List[str]:
    rem_symbols = r'\.|,'

    parts = re.split(r'\s+', name)
    parts = [p.lower() for p in parts]
    parts = [re.sub(rem_symbols, '', p) for p in parts]
    parts = [p for p in parts if p not in stop_words]

    return parts


def domain_2l(url: str) -> str:
    domain = urlparse(url).netloc
    return '.'.join(domain.split('.')[-2:])


def is_url_ignored(url: str, domain_stop_list: List[str]) -> bool:
    domain = domain_2l(url)
    return any([sw in domain for sw in domain_stop_list])


def find_matches(
        data: List[GoogleItem],
        match_functions: List[Callable[[CompanyInitialInfo, GoogleSearchListItem], bool]],
) -> List[List[str]]:
    ret = {}

    for row in data:
        ret[row.company.name] = None
        for mf in match_functions:
            match_was = False
            for sl in row.search_list:
                if mf(row.company, sl):
                    ret[row.company.name] = sl.href
                    match_was = True
                    break
            if match_was:
                break


    result_rows = [["Company", "Address", "Site"]]

    for row in data:
        result_rows.append([
            row.company.name,
            row.company.address,
            ret[row.company.name]
        ])

    return result_rows