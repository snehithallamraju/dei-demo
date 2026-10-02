#!/bin/sh
# Rehearsal / backup: builds everything in one go so ask.py works even if the live steps go wrong.
cd "$(dirname "$0")"
for f in sql/0*.sql; do duckdb demo.duckdb < "$f" > /dev/null || exit 1; done
echo "✅ demo.duckdb and data/orders_clean.parquet are ready"
