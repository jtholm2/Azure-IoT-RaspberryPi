module.exports = function (context, IoTHubMessage) {
    
    context.log(context.bindingData.systemPropertiesArray[0]["iothub-connection-device-id"]);
    var formattedMessage = JSON.parse(JSON.stringify(IoTHubMessage[0]));
    context.log(formattedMessage[0])

    var mongoClient = require('mongodb').MongoClient;
    const connString = process.env['COSMOS_MONGO_CONN_STRING'];
    const dbName = 'rpisurveylogs';
    const collectionName = context.bindingData.systemPropertiesArray[0]["iothub-connection-device-id"];
    
    const client = new mongoClient(connString, {useNewUrlParser: true, authSource: dbName});
    async function init() {
        context.log(client.isConnected()); // false
        await client.connect();
        context.log(client.isConnected()); // true
        var collection = client.db(dbName).collection(collectionName);
        
        try{
            await collection.insertMany(formattedMessage);
            context.log('inserted');
        } catch (err){
            context.log(err)
        }

        client.close();
        context.done();
    }
    init();
};