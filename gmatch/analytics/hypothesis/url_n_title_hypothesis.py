"""Check if any part of name contained in company url."""
from typing import List

from gmatch.analytics.hypothesis import get_company_stop_words, get_manual_stop_domains, find_matches, write_result_csv, \
    lemmatize_company, is_url_ignored
from gmatch.analytics.hypothesis.url_hypothesis import find_stop_domains, match_name_with_url
from gmatch.analytics.load_data import load_data
from gmatch.gmatch.items import CompanyInitialInfo, GoogleSearchListItem


def match_company_with_search_list_item(
        company: CompanyInitialInfo,
        sl: GoogleSearchListItem,
        stop_domains: List[str],
        company_stop_words: List[str]
) -> bool:

    if not sl.short_description:
        return False

    if is_url_ignored(sl.href, stop_domains):
        return False

    lcompany = ' '.join(lemmatize_company(company.name, company_stop_words))
    ldesc = ' '.join(lemmatize_company(sl.short_description, company_stop_words))

    return lcompany in ldesc



def run():
    data = load_data()
    stop_domains = find_stop_domains(data)

    stop_domains.extend(get_manual_stop_domains())
    stop_words = get_company_stop_words()

    def matcher1(company: CompanyInitialInfo, sl: GoogleSearchListItem) -> bool:
        return match_name_with_url(company.name, sl.href, stop_domains, stop_words)

    def matcher2(company: CompanyInitialInfo, sl: GoogleSearchListItem) -> bool:
        return match_company_with_search_list_item(company, sl, stop_domains, stop_words)

    result_rows = find_matches(data, [matcher1, matcher2])

    write_result_csv(result_rows, 'result_url_n_title_hypotesis.csv')

if __name__ == "__main__":
    run()





