from azure.cosmos import CosmosClient, PartitionKey
from config.settings import COSMOS_URL, COSMOS_KEY, DATABASE_NAME, CONTAINER_NAME

# Cosmos DB Setup
cosmos_client = CosmosClient(COSMOS_URL, COSMOS_KEY)
database = cosmos_client.create_database_if_not_exists(id=DATABASE_NAME)
container = database.create_container_if_not_exists(
    id=CONTAINER_NAME,
    partition_key=PartitionKey(path="/id"),
    offer_throughput=400
)