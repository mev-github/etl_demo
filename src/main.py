import argparse
import pandas as pd
from dpm.file_helper import FileHelper
from dpm.database_helper import DatabaseHelper
from processors.logs_parser import LogsParser


# def insert_unique_action_type(db_helper, action_type):
#     # Check if the action_type already exists
#     existing = db_helper.read_from_db('mysql',
#                                       f"SELECT action_type_id FROM action_types WHERE action_type = '{action_type}'")
#     if existing.empty:
#         # Insert new action type if not exists
#         new_df = pd.DataFrame({'action_type': [action_type]})
#         db_helper.write_to_db('mysql', new_df, 'action_types', if_exists='append')
#         # Fetch the newly inserted action_type_id
#         existing = db_helper.read_from_db('mysql',
#                                           f"SELECT action_type_id FROM action_types WHERE action_type = '{action_type}'")
#     return existing.iloc[0]['action_type_id']


def logs_parsing_pipeline():
    print("Running logs parsing pipeline...")
    # db_helper = DatabaseHelper()
    # db_helper.connect_mysql(host='localhost', port='3308', user='admin', password='admin', db='jenkins')

    csv_file_path = 'E:/Data/IDEA/etl_demo/tmp_data/4test.csv'
    df = FileHelper.read_csv(csv_file_path)

    for _, row in df.iterrows():
        parsed_log = LogsParser.parse_log(row['raw_str'])
        # action_type_id = insert_unique_action_type(db_helper, row['action_type'])

        log_entry = pd.DataFrame({
            'timestamp': [row['timestamp']],
            'user_id': [row['user_id']],
            # 'action_type_id': [action_type_id],
            'action_count': [row['action_count']],
            'parsed': [parsed_log]
        })
        print(log_entry.to_string(index=False))
        # db_helper.write_to_db('mysql', log_entry, 'activity_logs', if_exists='append')


def user_registration_pipeline():
    print("Running user registration pipeline...")
    # Placeholder for user registration processing logic


def main():
    parser = argparse.ArgumentParser(description="Run specific data processing pipelines.")
    parser.add_argument('--pipeline', type=str, help='The name of the pipeline to run')

    args = parser.parse_args()

    if args.pipeline == 'logs':
        logs_parsing_pipeline()
    elif args.pipeline == 'registration':
        user_registration_pipeline()
    else:
        print("Unknown pipeline. Please specify a valid pipeline name.")


if __name__ == "__main__":
    main()
