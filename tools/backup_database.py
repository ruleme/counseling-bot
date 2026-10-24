"""Take a consistent SQLite snapshot without printing counseling data."""
import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("source", type=Path)
parser.add_argument("destination", type=Path)
args = parser.parse_args()
if not args.source.is_file():
    parser.error("Source database does not exist")
if args.destination.exists():
    parser.error("Destination already exists; choose a new filename")
args.destination.parent.mkdir(parents=True, exist_ok=True)
with closing(sqlite3.connect(args.source.resolve().as_uri() + "?mode=ro", uri=True)) as source:
    with closing(sqlite3.connect(args.destination)) as destination:
        source.backup(destination)
print("Backup completed. Protect the snapshot as sensitive data.")
