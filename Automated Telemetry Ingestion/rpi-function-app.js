module.exports = function (context, IoTHubMessage) {
    //context.log(IoTHubMessage[0])
    var formattedMessage = JSON.parse(JSON.stringify(IoTHubMessage[0]))
    var mongoClient = require('mongodb').MongoClient;
    const connString = "{Insert MongoDb connection string here}";
    const dbName = '{Insert the database name here}';
    const collectionName = '{Insert the collection name here}';
    const client = new mongoClient(connString, {useNewUrlParser: true, authSource: dbName})
    async function init() {
        await client.connect();
        context.log(client.isConnected()); //should be true
        var collection = client.db(dbName).collection(collectionName);
        collection.insertMany(formattedMessage);
        client.close();
        context.done();
    }
    init();
};