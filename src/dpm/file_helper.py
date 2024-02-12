import pandas as pd


class FileHelper:
    @staticmethod
    def read_csv(file_path, **kwargs):
        try:
            return pd.read_csv(file_path, **kwargs)
        except Exception as e:
            print(f"Error reading CSV file {file_path}: {e}")
            return None

    @staticmethod
    def read_excel(file_path, **kwargs):
        try:
            return pd.read_excel(file_path, **kwargs)
        except Exception as e:
            print(f"Error reading Excel file {file_path}: {e}")
            return None

    @staticmethod
    def read_json(file_path, **kwargs):
        try:
            return pd.read_json(file_path, **kwargs)
        except Exception as e:
            print(f"Error reading JSON file {file_path}: {e}")
            return None

    @staticmethod
    def write_csv(df, file_path, **kwargs):
        try:
            df.to_csv(file_path, **kwargs)
        except Exception as e:
            print(f"Error writing CSV file to {file_path}: {e}")

    @staticmethod
    def write_excel(df, file_path, **kwargs):
        try:
            df.to_excel(file_path, **kwargs)
        except Exception as e:
            print(f"Error writing Excel file to {file_path}: {e}")

    @staticmethod
    def write_json(df, file_path, **kwargs):
        try:
            df.to_json(file_path, **kwargs)
        except Exception as e:
            print(f"Error writing JSON file to {file_path}: {e}")
