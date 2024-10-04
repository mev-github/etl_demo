db = db.getSiblingDB('mongo_db');

db.createUser({
    user: 'mongo_user',
    pwd: 'mongo_password',
    roles: [{ role: 'readWrite', db: 'mongo_db' }]
});

db.source_collection.insertMany([
    { column1: 'mongo_value1', column2: 'mongo_value2' },
    { column1: 'mongo_value3', column2: 'mongo_value4' }
]);
