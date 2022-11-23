# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from dataclasses import asdict
from pathlib import Path
from sqlite3 import OperationalError, IntegrityError

from itemadapter import ItemAdapter

import sqlite3 as sl

from gmatch.items import GoogleItem


class GmatchPipeline:
    def open_spider(self, sr):
        db_path = Path(__file__).parent.absolute() / "data" / "db"
        self.db = sl.connect(db_path)
        try:
            self.db.execute("""
                CREATE TABLE parsed(
                    company_name VARCHAR NOT NULL PRIMARY KEY ,
                    json  JSON
                );
            """)
        except OperationalError:
            pass

    def process_item(self, item: GoogleItem, spider):
        try:
            self.db.execute("INSERT INTO parsed(company_name, json) VALUES(?, ?)", (item.company.name, json.dumps(asdict(item))))
            self.db.commit()
        except IntegrityError:
            pass
        return None
