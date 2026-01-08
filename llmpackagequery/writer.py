from io import StringIO, TextIOWrapper
import csv
import logging
from typing import List
import os

log = logging.getLogger(__name__)

DEFAULT_PACKAGE_HEADER = ["package_name", "is_security_relevant", "explanation"]

class CSVResultsWriter:
    _csv_writer: csv.writer
    _file_dst: TextIOWrapper
    _package_header: List[str]
    _flush_counter: int = 0
    __FLUSH_BATCH_SIZE: int = 10

    def __init__(self,
                 file_dst: TextIOWrapper,
                 package_header: List[str] = DEFAULT_PACKAGE_HEADER) -> None:

        self._file_dst = file_dst
        self._package_header = package_header

    def _init_csv_file(self):
        try:
            # Write the header
            self._csv_writer.writerow(self._package_header)
        except:
            self.close()

    def __enter__(self):
        # Open and init the CSV file in write mode
        self._csv_writer = csv.writer(
            self._file_dst,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC)
        self._init_csv_file()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def write_results(self, results: str) -> None:
        # Use csv.reader to handle quoted content properly
        row = None
        try:
            result_reader = csv.reader(StringIO(results), delimiter=',', quotechar='"', skipinitialspace=True)
            row = next(result_reader)
            row = [col.strip() for col in row]
        except:
            log.error("skipping ...")
            row = None

        if row is None:
            log.error(f"Cannot parse results: {results}")
        else:
            self._csv_writer.writerow(row)
            self._flush_counter += 1

        # Flush the file every __FLUSH_BATCH_SIZE rows
        if not (self._flush_counter % self.__FLUSH_BATCH_SIZE):
            self._file_dst.flush()
            os.fsync(self._file_dst.fileno())

    # Close the file
    def close(self):
        if self._file_dst:
            self._file_dst.close()
