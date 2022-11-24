"""Check if any part of name contained in company url."""
from collections import Counter
from typing import List
from urllib.parse import urlparse

from gmatch.analytics.hypothesis import get_manual_stop_domains, write_result_csv, get_company_stop_words, find_matches, \
    lemmatize_company, domain_2l, is_url_ignored
from gmatch.analytics.load_data import load_data
from gmatch.gmatch.items import GoogleItem, CompanyInitialInfo, GoogleSearchListItem


def match_name_with_url(name: str, url: str, stop_domains: List[str], company_stop_words: List[str]) -> bool:
    if not url:
        return False

    if is_url_ignored(url, stop_domains):
        return False

    parts = lemmatize_company(name, company_stop_words)

    url_domain = domain_2l(url)

    return any([(p in url_domain) for p in parts])




def find_stop_domains(data: List[GoogleItem]) -> List[str]:

    domain_counter = Counter(sum([
        [
            domain_2l(sl.href) for sl in gi.search_list if sl.href
        ]
        for gi in data
    ], []))

    return [d for d, c in domain_counter.items() if c > 10]


def run():
    data = load_data()

    stop_domains = find_stop_domains(data)

    stop_domains.extend(get_manual_stop_domains())
    stop_words = get_company_stop_words()

    def matcher(company: CompanyInitialInfo, sl: GoogleSearchListItem) -> bool:
        return match_name_with_url(company.name, sl.href, stop_domains, stop_words)

    result_rows = find_matches(data, [matcher])

    write_result_csv(result_rows, 'result_url_hypotesis.csv')


if __name__ == "__main__":
    run()





