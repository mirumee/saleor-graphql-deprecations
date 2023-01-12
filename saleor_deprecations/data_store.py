import json
from pathlib import Path

import requests


class DataStore:
    def __init__(self, remote_url: str, local_path: Path):
        self.remote_url = remote_url.rstrip("/")
        self.local_path = local_path

    def get_remote(self, key: str):
        r = requests.get(f"{self.remote_url}/{key}.json")
        if r.status_code == 404:
            return None

        r.raise_for_status()
        return r.json()

    def set_local(self, key: str, data: dict | list):
        with open(self.local_path / f"{key}.json", "w+") as fp:
            json.dump(data, fp, indent=2)
