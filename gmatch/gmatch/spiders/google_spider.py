import csv
from pathlib import Path
from typing import List

import scrapy
from bs4 import BeautifulSoup
from scrapy.http import TextResponse

from gmatch.gmatch.items import CompanyInitialInfo, GoogleItem, GoogleSearchListItem


class GoogleSpider(scrapy.Spider):
    name = "gmatch"

    def start_requests(self):
        companies = self._get_companies()
        surl = lambda search_word, start: f'https://www.google.com/search?hl=en&q={search_word}&start={start}'
        for company in companies:
            for start in [0, 10]:
                yield scrapy.Request(surl(company.name + ' ' + company.address, start), meta={"company": company})
                yield scrapy.Request(surl(company.name, start), meta={"company": company})

    def parse(self, response: TextResponse) -> GoogleItem:
        yield self._parse_companies(response.text, response.meta["company"])

    def _parse_companies(self, html: str, company: CompanyInitialInfo) -> GoogleItem:
        bs = BeautifulSoup(html, "html.parser")
        h3s = bs.select("a h3")

        ret_list = []
        for r in h3s:
            root_el_children = list(r.parent.parent.parent.parent.children)
            item = GoogleSearchListItem(
                href=r.parent.attrs.get("href"),
                title=r.text,
                short_description=root_el_children[1].text if len(root_el_children) >= 2 else None
            )
            ret_list.append(item)

        return GoogleItem(
            company=company,
            search_list=ret_list
        )

    def _get_companies(self) -> List[CompanyInitialInfo]:
        path = Path(__file__).parent.absolute() / "data" / "companies.csv"

        if not path.exists():
            raise Exception(f"{path} does not exists. But it please before running script")

        rows = []
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for r in reader:
                rows.append(r)

        rows = rows[1:]
        rows = [r for r in rows if len(r) == 3]

        problem_rows = [
            r
            for r in rows
            if
                not type(r[0]) is str or
                not r[0].strip()
        ]

        if len(problem_rows):
            problem_rows_str = "\n".join([", ".join(r) for r in problem_rows])
            raise Exception("""
                companies.csv must have next structure:
                
                Company Name,,Company Address
                Some Name,,"Some address"
                
                Rows with problems:
                %s
            """ % problem_rows_str)

        return [
            CompanyInitialInfo(
                name=r[0],
                address=r[2]
            )
            for r in rows
        ]