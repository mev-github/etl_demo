import logging

import pandas as pd


class DataProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("DataProcessor initialized")

    def process_data(self, df, columns_to_select=None) -> pd.DataFrame:
        self.logger.info("Processing data...")
        try:
            # Apply all transformations in an efficient sequence
            df = self._remove_empty_and_archived_rows(df)
            df = self._select_useful_data_and_remove_duplicates(df, columns_to_select)
            return df
        except Exception as e:
            self.logger.error(f"An error occurred during data processing: {e}")
            raise

    def _remove_empty_and_archived_rows(self, df) -> pd.DataFrame:
        # Combine empty row removal and filtering non-archived rows in one step
        initial_count = len(df)
        df = df.dropna(how='all')  # Remove entirely empty rows
        df = df[df['action_count'] != 0]  # Remove rows where action_count is 0
        df = df[df['action_type'].notnull()]  # Remove rows where action_type is missing
        df = df[df['action_type'] != 'archive']  # Keep only archived rows
        final_count = len(df)
        self.logger.info(f"Filtered from {initial_count} to {final_count} rows")
        return df

    def _select_useful_data_and_remove_duplicates(self, df, columns_to_select=None) -> pd.DataFrame:
        # Specify default columns directly in the method signature for better clarity and performance
        if columns_to_select is None:
            columns_to_select = ['guid', 'email', 'action_type', 'action_count']
        # Select columns and remove duplicates in one step
        return df.loc[:, columns_to_select].drop_duplicates()
