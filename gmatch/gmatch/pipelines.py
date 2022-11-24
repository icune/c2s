# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from dataclasses import asdict
from pathlib import Path
from sqlite3 import OperationalError, IntegrityError

import sqlite3 as sl

from gmatch.gmatch.items import GoogleItem


class GmatchPipeline:
    def open_spider(self, sr):
        db_path = Path(__file__).parent.absolute() / "data" / "db"
        self.db = sl.connect(db_path)
        self.cache = {}
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
        self.cache[item.company.name] = [
            *[item],
            *self.cache.get(item.company.name, [])
        ]
        if len(self.cache[item.company.name]) == 4:
            aggregated = GoogleItem(
                company=item.company,
                search_list=sum([it.search_list for it in self.cache[item.company.name]], [])
            )

            self._insert_record(aggregated)
            self._print_total()
        return None

    def close_spider(self, sp):
        print("Finalizing")
        for k, v in self.cache.items():
            if len(v) < 4:
                aggregated = GoogleItem(
                    company=v[0].company,
                    search_list=sum([it.search_list for it in v], [])
                )
                self._insert_record(aggregated)
        self._print_total()

    def _insert_record(self, item: GoogleItem):
        try:
            self.db.execute("INSERT INTO parsed(company_name, json) VALUES(?, ?)",
                            (item.company.name, json.dumps(asdict(item))))
            self.db.commit()
        except IntegrityError:
            pass

    def _print_total(self):
        cursor = self.db.execute("SELECT COUNT(*) FROM parsed")
        ret = cursor.fetchone()
        print("%3d processed" % ret[0])
