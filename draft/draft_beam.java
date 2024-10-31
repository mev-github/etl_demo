PipelineOptions options = PipelineOptionsFactory.create();
Pipeline p = Pipeline.create(options);

// Read from PostgreSQL
PCollection<Row> postgresRows = p.apply("ReadFromPostgres", JdbcIO.<Row>read()
        .withDataSourceConfiguration(JdbcIO.DataSourceConfiguration.create(
                        "org.postgresql.Driver", "jdbc:postgresql://postgres:5432/postgres_db")
                .withUsername("postgres_user")
                .withPassword("postgres_password"))
        .withQuery("SELECT * FROM source_table")
        .withRowMapper(new JdbcIO.RowMapper<Row>() {
            public Row mapRow(ResultSet resultSet) throws Exception {
                // Map ResultSet to Row or custom object
            }
        }));

// Read from local files
PCollection<String> fileRows = p.apply("ReadFromCSV", TextIO.read().from("data/input_file.csv"));

// Combine data sources
PCollection<MyRecord> allRecords = PCollectionList.of(postgresRows).and(fileRows)
        .apply("Flatten", Flatten.pCollections());

// Transformation
PCollection<MyRecord> transformedRecords = allRecords.apply("TransformRecords", ParDo.of(new DoFn<MyRecord, MyRecord>() {
    @ProcessElement
    public void processElement(ProcessContext c) {
        MyRecord record = c.element();
        record.setId(null); // Remove 'id' field
        record.setMetaId(UUID.randomUUID().toString());
        c.output(record);
    }
}));

// Remove duplicates
PCollection<MyRecord> uniqueRecords = transformedRecords.apply("RemoveDuplicates", Distinct.create());

// Write to MySQL
uniqueRecords.apply("WriteToMySQL", JdbcIO.<MyRecord>write()
    .withDataSourceConfiguration(JdbcIO.DataSourceConfiguration.create(
        "com.mysql.jdbc.Driver", "jdbc:mysql://mysql:3306/mysql_db")
        .withUsername("mysql_user")
        .withPassword("mysql_password"))
        .withStatement("INSERT INTO final_table (...) VALUES (...)")
    .withPreparedStatementSetter(new JdbcIO.PreparedStatementSetter<MyRecord>() {
    public void setParameters(MyRecord record, PreparedStatement query) throws SQLException {
        // Set parameters in query
    }
}));

        p.run().waitUntilFinish();
