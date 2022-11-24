# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from pydantic.dataclasses import dataclass
from typing import List, Optional


@dataclass
class CompanyInitialInfo:
    name: str
    address: str


@dataclass
class CompanyExtendedInfo:
    url: str


@dataclass
class GoogleSearchListItem:
    href: Optional[str]
    title: Optional[str]
    short_description: Optional[str]


@dataclass
class GoogleItem:
    company: CompanyInitialInfo
    search_list: List[GoogleSearchListItem]
