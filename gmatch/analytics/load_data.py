import json
import sqlite3
from pathlib import Path
from typing import List

from gmatch.gmatch.items import GoogleItem


def load_data() -> List[GoogleItem]:
    db_path = Path(__file__).parent.absolute() / "../gmatch/data/db"
    if not  db_path.is_file():
        raise FileNotFoundError(f"{db_path} sqlite database not found")
    db = sqlite3.connect(db_path)

    cursor = db.execute("SELECT * FROM parsed")
    raw = cursor.fetchall()
    return [GoogleItem(**json.loads(r[1])) for r in raw]

if __name__ == "__main__":
    print(load_data())
