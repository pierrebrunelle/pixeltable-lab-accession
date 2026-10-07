"""Seed stations and a first batch of samples.

Usage:
    python seed.py            # seeds the local `lab` catalog directory
    python seed.py my_dir     # or another directory you passed to `pxt schema update`
"""
import sys
from pathlib import Path

import pixeltable as pxt

target = sys.argv[1] if len(sys.argv) > 1 else 'lab'
HERE = Path(__file__).resolve().parent

SEED = {
    'stations': [
        {'station_id': 'HEM-1', 'name': 'Hematology', 'capacity': 40},
        {'station_id': 'CHEM-2', 'name': 'Chemistry', 'capacity': 60},
        {'station_id': 'MICRO-1', 'name': 'Microbiology', 'capacity': 15},
    ],
    'samples': [
        {'accession_id': 'A-0001', 'specimen': 'whole blood', 'priority': 3, 'received_at': '2026-09-28T07:58', 'batch_code': 'B-MORNING'},
        {'accession_id': 'A-0002', 'specimen': 'serum', 'priority': 1, 'received_at': '2026-09-28T08:03', 'batch_code': 'B-MORNING'},
        {'accession_id': 'A-0003', 'specimen': 'urine', 'priority': 2, 'received_at': '2026-09-28T08:10', 'batch_code': None},
    ],
}

for table_name, rows in SEED.items():
    t = pxt.get_table(f'{target}/{table_name}')
    if t.count() > 0:
        print(f'{target}/{table_name} already has {t.count()} rows; skipping')
        continue
    for row in rows:
        for k, v in row.items():
            if isinstance(v, str) and v.startswith('data/'):
                row[k] = str(HERE / v)   # local sample media file
    t.insert(rows)
    print(f'inserted {len(rows)} rows into {target}/{table_name}')
