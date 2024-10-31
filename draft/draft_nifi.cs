// Extract data from PostgreSQL
using Npgsql;
using MongoDB.Driver;
using MySqlConnector;
using CsvHelper;

// Extraction from PostgreSQL
var pgConnString = "Host=postgres;Port=5432;Username=postgres_user;Password=postgres_password;Database=postgres_db";
using var pgConn = new NpgsqlConnection(pgConnString);
pgConn.Open();
var pgCmd = new NpgsqlCommand("SELECT * FROM source_table", pgConn);
var pgReader = pgCmd.ExecuteReader();
var pgDataTable = new DataTable();
pgDataTable.Load(pgReader);

// Extraction from MongoDB
var mongoClient = new MongoClient("mongodb://mongo_user:mongo_password@mongodb:27017");
var mongoDb = mongoClient.GetDatabase("mongo_db");
var mongoCollection = mongoDb.GetCollection<BsonDocument>("source_collection");
var mongoData = mongoCollection.Find(FilterDefinition<BsonDocument>.Empty).ToList();

// Read local CSV file
using var reader = new StreamReader("data/input_file.csv");
using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);
var csvData = csv.GetRecords<dynamic>().ToList();

// Transformation
var allData = new List<dynamic>();
allData.AddRange(pgDataTable.AsEnumerable().Select(row => row.ItemArray));
allData.AddRange(mongoData);
allData.AddRange(csvData);

// Remove duplicates, drop 'id' column, add 'meta_id'
var transformedData = allData
    .Select(record => {
        var dict = record as IDictionary<string, object>;
        dict.Remove("id");
        dict["meta_id"] = Guid.NewGuid();
        return dict;
    })
    .GroupBy(record => record["meta_id"]) // Assuming 'meta_id' ensures uniqueness
    .Select(group => group.First())
    .ToList();

// Load into MySQL
var mySqlConnString = "Server=mysql;Database=mysql_db;User=mysql_user;Password=mysql_password;";
using var mySqlConn = new MySqlConnection(mySqlConnString);
mySqlConn.Open();
foreach (var record in transformedData)
{
    var cmd = new MySqlCommand("INSERT INTO final_table (...) VALUES (...)", mySqlConn);
    // Add parameters to cmd
    cmd.ExecuteNonQuery();
}
