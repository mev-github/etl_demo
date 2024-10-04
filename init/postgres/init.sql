CREATE TABLE source_table (
                              id SERIAL PRIMARY KEY,
                              column1 VARCHAR(255),
                              column2 VARCHAR(255)
);

INSERT INTO source_table (column1, column2) VALUES
                                                ('postgres_value1', 'postgres_value2'),
                                                ('postgres_value3', 'postgres_value4');
