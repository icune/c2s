from typing import List

from gmatch.gmatch.items import GoogleItem


def check_integrity(parsed_companies: List[GoogleItem]) -> None:
    missed_companies = []
    for parsed_company in parsed_companies:
        not_parsed = all([sl.href is None for sl in parsed_company.search_list])
        if not_parsed:
            missed_companies.append(parsed_company)
    if missed_companies:
        raise Exception(
            "Data not parsed for next companies: %s" %
            ', '.join([mc.company.name for mc in missed_companies])
        )
