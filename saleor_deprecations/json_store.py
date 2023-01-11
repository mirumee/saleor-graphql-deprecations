import json
from datetime import datetime
from pathlib import Path

import requests


class JsonStore:
    def __init__(self, prefix: str, index_name: str, remote_url: str, data_dir: Path):
        self.prefix = prefix
        self.remote_url = remote_url.rstrip("/")
        self.data_dir = data_dir

        self.index_name = index_name
        self.index = self.load_remote_index()

    def load_remote_index(self):
        r = requests.get(f"{self.remote_url}/{self.index_name}.json")
        return r.json()

    def load_last_entry(self):
        if not self.index:
            return None

        last_id = self.index[-1]
        r = requests.get(f"{self.remote_url}/{last_id}.json")
        return r.json()

    def save_index(self):
        with open(self.data_dir / f"{self.index_name}.json", "w+") as fp:
            json.dump(self.index, fp, indent=2)

    def insert(self, data: dict) -> str:
        entry_id = "%s-%s" % (self.prefix, datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.index.append(entry_id)

        with open(self.data_dir / f"{entry_id}.json", "w+") as fp:
            json.dump(data, fp, indent=2)

        return entry_id
