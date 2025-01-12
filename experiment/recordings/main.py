import sqlite3
import pandas as pd
import os
from pathlib import Path
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('db_merger.log'),
        logging.StreamHandler()
    ]
)


def get_paired_databases(data_dir):
    """
    Finds and pairs database files based on their numeric suffix.

    Args:
        data_dir (str): Path to the directory containing database files

    Returns:
        list: List of tuples containing paired database paths (otree_db, hr_db)
    """
    data_path = Path(data_dir)

    # Get all database files
    db_files = list(data_path.glob("*.db"))
    sqlite3_files = list(data_path.glob("*.sqlite3"))

    # Extract numbers from filenames and create pairs
    pairs = []
    for db_file in db_files:
        # Extract number from filename (e.g., "file-1.db" -> "1")
        db_num = re.search(r'-(\d+)\.db$', db_file.name)
        if db_num:
            num = db_num.group(1)
            # Find matching sqlite3 file
            matching_sqlite3 = next(
                (f for f in sqlite3_files if f.name.endswith(f'-{num}.sqlite3')),
                None
            )
            if matching_sqlite3:
                pairs.append((db_file, matching_sqlite3))
                logging.info(f"Paired databases: {db_file.name} <-> {matching_sqlite3.name}")

    return pairs


def merge_pair_to_temp(otree_db, hr_db, temp_db):
    """
    Merges a pair of databases into a temporary database.

    Args:
        otree_db (Path): Path to otree database
        hr_db (Path): Path to HR database
        temp_db (str): Path for temporary merged database
    """
    # Create new temporary database
    if os.path.exists(temp_db):
        os.remove(temp_db)

    # Copy all tables from both databases
    for src_db, src_type in [(otree_db, 'oTree'), (hr_db, 'HR')]:
        try:
            src_conn = sqlite3.connect(src_db)
            dest_conn = sqlite3.connect(temp_db)

            # Get all tables
            cursor = src_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            # Copy each table
            for table_info in tables:
                table_name = table_info[0]
                df = pd.read_sql_query(f"SELECT * FROM {table_name}", src_conn)
                df.to_sql(table_name, dest_conn, index=False, if_exists='append')
                logging.info(f"Copied table {table_name} from {src_type} database {src_db.name}")

            src_conn.close()
            dest_conn.close()

        except sqlite3.Error as e:
            logging.error(f"Error processing {src_db}: {str(e)}")
            continue


def execute_sql_script(db_path, script_path):
    """
    Executes SQL script on a database.

    Args:
        db_path (str): Path to the database
        script_path (str): Path to the SQL script
    """
    try:
        with open(script_path, 'r') as file:
            sql_script = file.read()

        conn = sqlite3.connect(db_path)
        conn.executescript(sql_script)
        conn.commit()
        conn.close()
        logging.info(f"Successfully executed SQL script on {db_path}")

    except (sqlite3.Error, IOError) as e:
        logging.error(f"Error executing SQL script: {str(e)}")


def merge_final_tables(temp_dbs, final_db):
    """
    Merges specified tables from all temporary databases into final database.

    Args:
        temp_dbs (list): List of temporary database paths
        final_db (str): Path for final merged database
    """
    tables_to_merge = [
        'math_task_table',
        'ball_task_table',
        'video_one_table',
        'video_two_table'
    ]

    if os.path.exists(final_db):
        os.remove(final_db)

    final_conn = sqlite3.connect(final_db)

    for table in tables_to_merge:
        combined_data = pd.DataFrame()

        for temp_db in temp_dbs:
            try:
                temp_conn = sqlite3.connect(temp_db)
                df = pd.read_sql_query(f"SELECT * FROM {table}", temp_conn)
                combined_data = pd.concat([combined_data, df], ignore_index=True)
                temp_conn.close()
            except sqlite3.Error as e:
                logging.error(f"Error reading {table} from {temp_db}: {str(e)}")
                continue

        if not combined_data.empty:
            # Reset index if there's an 'id' column
            if 'id' in combined_data.columns:
                combined_data = combined_data.drop('id', axis=1)

            combined_data.to_sql(table, final_conn, index=True, index_label='id')
            logging.info(f"Merged {table} with {len(combined_data)} total rows")

    final_conn.close()


def process_databases():
    """
    Main function to process all databases.
    """
    # Get paired databases
    pairs = get_paired_databases('data')
    if not pairs:
        logging.error("No paired databases found!")
        return

    # Create temporary databases for each pair
    temp_dbs = []
    for i, (otree_db, hr_db) in enumerate(pairs):
        temp_db = f"temp_merged_{i}.sqlite3"
        temp_dbs.append(temp_db)

        # Merge pair into temporary database
        logging.info(f"\nProcessing pair {i + 1}: {otree_db.name} and {hr_db.name}")
        merge_pair_to_temp(otree_db, hr_db, temp_db)

        # Execute create_tables.sql on temporary database
        execute_sql_script(temp_db, 'create_tables.sql')

    # Merge all temporary databases into final database
    final_db = "final_merged.sqlite3"
    logging.info("\nCreating final merged database...")
    merge_final_tables(temp_dbs, final_db)

    # Clean up temporary databases
    for temp_db in temp_dbs:
        if os.path.exists(temp_db):
            os.remove(temp_db)
            logging.info(f"Removed temporary database: {temp_db}")

    logging.info("\nDatabase merge completed successfully!")
    logging.info(f"Final database: {final_db}")


if __name__ == "__main__":
    process_databases()