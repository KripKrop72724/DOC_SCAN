import cx_Oracle
import logging
import multiprocessing
import time

import pandas as pd
from pymongo import MongoClient
from termcolor import colored

from MONGO_CRED import DB_URL, DB_PASSWORD, DB_USERNAME, dsn_tns


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _log_cycle_header(cycle: int) -> None:
    """Log a highlighted header for each clone cycle."""
    logger.info(colored(f"\n=== Clone Cycle {cycle} ===", "cyan", attrs=["bold"]))


def _log_cycle_stats(
    prep_duration: float, row_count: int, fetch_duration: float, cycle_duration: float
) -> None:
    """Log a table summarizing stats for the completed cycle."""
    stats = [
        ("Collection prep (s)", f"{prep_duration:.2f}"),
        ("Rows inserted", str(row_count)),
        ("Fetch duration (s)", f"{fetch_duration:.2f}"),
        ("Total cycle time (s)", f"{cycle_duration:.2f}"),
    ]

    name_width = max(len(name) for name, _ in stats)
    value_width = max(len(value) for _, value in stats)
    border = "+" + "-" * (name_width + 2) + "+" + "-" * (value_width + 2) + "+"
    logger.info(border)
    logger.info(f"| {'Metric'.ljust(name_width)} | {'Value'.ljust(value_width)} |")
    logger.info(border)
    for name, value in stats:
        logger.info(f"| {name.ljust(name_width)} | {value.rjust(value_width)} |")
    logger.info(border)


def _log_credentials_table(records: list) -> None:
    """Log a table of all usernames and passwords cloned."""
    if not records:
        logger.info("No credentials were cloned.")
        return
    df = pd.DataFrame(records, columns=["USERNAME", "PASSWORD"])
    logger.info("\n" + df.to_string(index=False))


def clone_mongo():
    cycle = 0
    while True:
        cycle += 1
        cycle_start = time.time()
        _log_cycle_header(cycle)
        time.sleep(3)

        logger.info(colored("Connecting to MongoDB and preparing collection", "yellow"))
        prep_start = time.time()
        my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
        collection = my_client["DOC_SCAN"]
        doc_id = collection['AUTH']
        doc_id.drop()
        prep_duration = time.time() - prep_start
        logger.info(colored(f"Collection ready in {prep_duration:.2f}s", "green"))

        time.sleep(1.5)
        cursor = dsn_tns.cursor()

        query = "select username , password  from cdr.api_users"

        logger.info(colored("Fetching records from Oracle", "yellow"))
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
        logger.info(
            colored(
                f"Fetched and inserted {row_count} records in {fetch_duration:.2f}s",
                "green",
            )
        )

        duration = time.time() - cycle_start
        _log_cycle_stats(prep_duration, row_count, fetch_duration, duration)
        logger.info(colored("Cycle complete", "cyan"))


def clone_mongo_once():
    """Clone credentials from Oracle to MongoDB a single time."""
    cycle_start = time.time()
    _log_cycle_header(1)
    time.sleep(3)

    logger.info(colored("Connecting to MongoDB and preparing collection", "yellow"))
    prep_start = time.time()
    my_client = MongoClient(DB_URL % (DB_USERNAME, DB_PASSWORD))
    collection = my_client["DOC_SCAN"]
    doc_id = collection['AUTH']
    doc_id.drop()
    prep_duration = time.time() - prep_start
    logger.info(colored(f"Collection ready in {prep_duration:.2f}s", "green"))

    time.sleep(1.5)
    cursor = dsn_tns.cursor()

    query = "select username , password  from cdr.api_users"

    logger.info(colored("Fetching records from Oracle", "yellow"))
    fetch_start = time.time()
    row_count = 0
    records = []
    for row in cursor.execute(query):
        df = pd.DataFrame(row, index=["USERNAME", "PASSWORD"])
        result = {
            "USERNAME": df.iloc[0][0],
            "PASSWORD": df.iloc[1][0]
        }
        doc_id.insert_one(result)
        records.append(result)
        row_count += 1
    fetch_duration = time.time() - fetch_start
    logger.info(
        colored(
            f"Fetched and inserted {row_count} records in {fetch_duration:.2f}s",
            "green",
        )
    )

    _log_credentials_table(records)

    duration = time.time() - cycle_start
    _log_cycle_stats(prep_duration, row_count, fetch_duration, duration)
    logger.info(colored("Clone complete", "cyan"))


def initiate_mongo_devil():
    cm = multiprocessing.Process(target=clone_mongo, daemon=True)
    cm.start()

if __name__ == '__main__':
    clone_mongo_once()
