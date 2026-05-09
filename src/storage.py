import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Set

from src.verify import VALIDITY, PROVIDERS_TYPE


def create_directory(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def create_file(path: str) -> None:
    parent_directory = os.path.dirname(os.path.abspath(path))
    create_directory(parent_directory)
    if not os.path.exists(path):
        with open(path, "w") as _file:
            pass


def print_err(s):
    print(s, file=sys.stderr)


def save_processing_state(output_path: str, keyword: str, page_number: int) -> None:
    state_dir = os.path.join(output_path, "state")
    os.makedirs(state_dir, exist_ok=True)
    state_path = os.path.join(state_dir, f"{round(time.time())}.json")
    state = {
        "keyword": keyword,
        "last_page": page_number,
        "updated_at": datetime.now().strftime("%H:%M:%S on %B %d, %Y"),
    }
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)


class ScannedDb:
    """
    File backed database of scanned gist IDs. Stores one gist per line.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        create_file(file_path)
        self.scanned: Set[str] = set()
        self.load()

    def load(self) -> None:
        try:
            with open(self.file_path, "r") as f:
                for line in f:
                    gist_id = line.strip()
                    if gist_id != "":
                        self.scanned.add(gist_id)
        except FileNotFoundError:
            print_err("Database file not found.")

    def seen(self, gist_id: str) -> bool:
        return gist_id in self.scanned

    def add(self, gist_id: str) -> None:
        if gist_id in self.scanned:
            return
        self.scanned.add(gist_id)
        with open(self.file_path, "a") as file:
            file.write(gist_id + "\n")


def generate_message(provider: PROVIDERS_TYPE, gist_id: str, owner: str) -> str:
    return (
        f"Hello @{owner},\n"
        "This is an automated message generated to inform you that "
        f"we have detected a potentially active {provider} API key "
        f"exposed in your GitHub Gist: https://gist.github.com/{owner}/{gist_id}.\n"
        "Please revoke the key immediately and delete the gist.\n"
        "This action was performed by aerovato/keyscan. "
        "For more information, please contact @kevinMEH. "
        "If you find our service helpful, please consider following and shouting out @kevinMEH."
    )


def save_record(
    output_dir: str,
    gist_id: str,
    owner: str,
    provider: PROVIDERS_TYPE,
    confidence: str,
    validity: VALIDITY,
    line: str,
) -> str:
    """
    Save an exposure record for additional verification.

    Will save to: {output_dir}/{validity}/{gist_id}.json
    """
    record: Dict = {
        "gist_id": gist_id,
        "owner": owner,
        "url": f"https://gist.github.com/{owner}/{gist_id}",
        "message": generate_message(provider, gist_id, owner),
        "provider": provider,
        "confidence": confidence,
        "validity": validity,
        "line": line,
        "created_at": datetime.now().strftime("%H:%M:%S on %B %d, %Y"),
    }

    write_directory = os.path.join(output_dir, validity)
    create_directory(write_directory)
    file_path = os.path.join(
        write_directory, f"{owner}_{gist_id}_{os.urandom(8).hex()}.json"
    )
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=4)

    return file_path
