import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import uuid

# Define pipeline options
options = PipelineOptions()

# Define the transformation function
def transform_record(record):
    record.pop('id', None)
    record['meta_id'] = str(uuid.uuid4())
    return record

# Create the pipeline
with beam.Pipeline(options=options) as p:
    # Read from PostgreSQL
    postgres_rows = (
            p
            | 'ReadFromPostgres' >> beam.io.Read(
        beam.io.jdbc.JdbcIO.read(
            driver_class_name='org.postgresql.Driver',
            jdbc_url='jdbc:postgresql://postgres:5432/postgres_db',
            username='postgres_user',
            password='postgres_password',
            query='SELECT * FROM source_table',
        )
    )
    )

    # Read from MongoDB (requires custom IO or external library)
    mongodb_rows = (
            p
            | 'ReadFromMongoDB' >> beam.Create([])  # Replace with actual MongoDB read
    )

    # Read from local CSV files
    file_rows = (
            p
            | 'ReadFromCSV' >> beam.io.ReadFromText('data/input_file.csv', skip_header_lines=1)
            | 'ParseCSV' >> beam.Map(lambda line: dict(zip(['field1', 'field2'], line.split(','))))
    )

    # Combine all data sources
    all_records = (
            (postgres_rows, mongodb_rows, file_rows)
            | 'Flatten' >> beam.Flatten()
    )

    # Transform data
    transformed_records = (
            all_records
            | 'TransformRecords' >> beam.Map(transform_record)
            | 'RemoveDuplicates' >> beam.Distinct()
    )

    # Write to MySQL
    transformed_records | 'WriteToMySQL' >> beam.io.Write(
        beam.io.jdbc.JdbcIO.write(
            driver_class_name='com.mysql.jdbc.Driver',
            jdbc_url='jdbc:mysql://mysql:3306/mysql_db',
            username='mysql_user',
            password='mysql_password',
            statement='INSERT INTO final_table (columns...) VALUES (?, ?, ?)',
            # Map record fields to columns
            prepared_statement_fn=lambda record: [record['field1'], record['field2'], record['meta_id']],
        )
    )
