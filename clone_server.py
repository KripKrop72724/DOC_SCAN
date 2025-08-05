import cx_Oracle
import multiprocessing
import time

import pandas as pd
from pymongo import MongoClient
from termcolor import colored

from MONGO_CRED import DB_URL, DB_PASSWORD, DB_USERNAME, dsn_tns


def _print_cycle_header(cycle: int) -> None:
    """Print a highlighted header for each clone cycle."""
    print(colored(f"\n=== Clone Cycle {cycle} ===", "cyan", attrs=["bold"]))


def _print_cycle_stats(
    prep_duration: float, row_count: int, fetch_duration: float, cycle_duration: float
) -> None:
    """Print a table summarizing stats for the completed cycle."""
    stats = [
        ("Collection prep (s)", f"{prep_duration:.2f}"),
        ("Rows inserted", str(row_count)),
        ("Fetch duration (s)", f"{fetch_duration:.2f}"),
        ("Total cycle time (s)", f"{cycle_duration:.2f}"),
    ]

    name_width = max(len(name) for name, _ in stats)
    value_width = max(len(value) for _, value in stats)
    border = "+" + "-" * (name_width + 2) + "+" + "-" * (value_width + 2) + "+"
    print(border)
    print(f"| {'Metric'.ljust(name_width)} | {'Value'.ljust(value_width)} |")
    print(border)
    for name, value in stats:
        print(f"| {name.ljust(name_width)} | {value.rjust(value_width)} |")
    print(border)


def clone_mongo():
    cycle = 0
    while True:
        cycle += 1
        cycle_start = time.time()
        _print_cycle_header(cycle)
        time.sleep(3)

        print(colored("Connecting to MongoDB and preparing collection", "yellow"))
        prep_start = time.time()
        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc_id = collection['AUTH']
        doc_id.drop()
        prep_duration = time.time() - prep_start
        print(colored(f"Collection ready in {prep_duration:.2f}s", "green"))

        time.sleep(1.5)
        cursor = dsn_tns.cursor()

        query = "select cdr.api_users.username , cdr.api_users.password  from cdr.api_users"

        print(colored("Fetching records from Oracle", "yellow"))
        fetch_start = time.time()
        row_count = 0
        for row in cursor.execute(query):
            df = pd.DataFrame(row, index=["USERNAME", "PASSWORD"])
            result = {
                "USERNAME": df.iloc[0][0],
                "PASSWORD": df.iloc[1][0]
            }
            doc_id.insert_one(result)
            row_count += 1
        fetch_duration = time.time() - fetch_start
        print(
            colored(
                f"Fetched and inserted {row_count} records in {fetch_duration:.2f}s",
                "green",
            )
        )

        duration = time.time() - cycle_start
        _print_cycle_stats(prep_duration, row_count, fetch_duration, duration)
        print(colored("Cycle complete", "cyan"))


def initiate_mongo_devil():
    cm = multiprocessing.Process(target=clone_mongo, daemon=True)
    cm.start()
