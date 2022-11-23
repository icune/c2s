import csv
from pathlib import Path
from typing import List

import scrapy
from bs4 import BeautifulSoup
from scrapy.http import TextResponse

from gmatch.items import CompanyInitialInfo, GoogleItem, GoogleSearchListItem


class GoogleSpider(scrapy.Spider):
    name = "gmatch"

    def start_requests(self):
        companies = self._get_companies()
        surl = lambda x: f'https://www.google.com/search?hl=en&q={x}'
        for company in companies:
            yield scrapy.Request(surl(company.name), meta={"company": company})

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

        rows = []
        with open(path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for r in reader:
                rows.append(r)

        rows = rows[1:]

        return [
            CompanyInitialInfo(
                name=r[0],
                address=r[2]
            )
            for r in rows
        ]