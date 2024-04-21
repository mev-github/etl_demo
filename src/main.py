import argparse
import logging

import yaml
from tabulate import tabulate

from dpu.data_processor import DataProcessor
from dpu.data_reader import DataReader
from dpu.data_writer import DataWriter


class DataProcessing:
    def __init__(self, config_path='config/settings.yaml'):
        self.config_path = config_path
        self._settings = self.load_settings()
        self._args = self.parse_arguments()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_settings(self):
        with open(self.config_path, 'r') as file:
            settings = yaml.safe_load(file)
        return settings

    def parse_arguments(self):
        parser = argparse.ArgumentParser(description='Data Processing Script')
        parser.add_argument('-r', '--read', help='Source type (file or table)')
        parser.add_argument('-rt', '--read_type', help='Source file format or database type')
        parser.add_argument('-rn', '--read_name', help='File path or table name')
        parser.add_argument('-w', '--write', help='Destination type (file or table)')
        parser.add_argument('-wt', '--write_type', help='Destination file format or database type')
        parser.add_argument('-wn', '--write_name', help='File path or table name')
        args = parser.parse_args()

        # Override defaults with any command-line arguments provided
        if args.read:
            self._settings['source']['type'] = args.read
        if args.read_type:
            self._settings['source']['format'] = args.read_type
        if args.read_name:
            self._settings['source']['name'] = args.read_name
        if args.write:
            self._settings['destination']['type'] = args.write
        if args.write_type:
            self._settings['destination']['format'] = args.write_type
        if args.write_name:
            self._settings['destination']['name'] = args.write_name

        return args

    def run(self):
        try:
            logging.info("Reading data...")
            reader = DataReader()
            df = reader.read_data(self._settings['source']['type'], self._settings['source']['format'],
                                  self._settings['source']['name'])

            logging.info("Cleaning and filtering data...")
            processor = DataProcessor()
            filtered_df = processor.process_data(df)

            if 'type' not in self._settings['destination'] or self._settings['destination']['type'] is None:
                logging.info(tabulate(filtered_df.head(5), headers='keys', tablefmt='psql'))
                logging.info("Process completed successfully.")
                return

            logging.info("Writing data...")
            writer = DataWriter()
            writer.write_data(filtered_df, self._settings['destination']['type'],
                              self._settings['destination']['format'], self._settings['destination']['name'])
            logging.info(f"Process completed successfully for rows: {len(filtered_df)}")

        except Exception as e:
            logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    data_processing = DataProcessing()
    data_processing.run()
