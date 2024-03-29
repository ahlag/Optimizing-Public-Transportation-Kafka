"""Producer base-class providing common utilites and functionality"""
import logging
import time


from confluent_kafka import avro
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.avro import AvroProducer

logger = logging.getLogger(__name__)

BROKER_URL = "PLAINTEXT://localhost:9092"
SCHEMA_REGISTRY_URL = "http://localhost:8081"

class Producer:
    """Defines and provides common functionality amongst Producers"""

    # Tracks existing topics across all Producer instances
    existing_topics = set([])

    def __init__(
        self,
        topic_name,
        key_schema,
        value_schema=None,
        num_partitions=1,
        num_replicas=1,
    ):
        """Initializes a Producer object with basic settings"""
        self.topic_name = topic_name
        self.key_schema = key_schema
        self.value_schema = value_schema
        self.num_partitions = num_partitions
        self.num_replicas = num_replicas

        #
        #
        # TODO: Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry!
        #
        #
        self.broker_properties = {
            "bootstrap.servers": BROKER_URL,
            "schema.registry.url": SCHEMA_REGISTRY_URL,
        }

        # If the topic does not already exist, try to create it
        if self.topic_name not in Producer.existing_topics:
            self.create_topic()
            Producer.existing_topics.add(self.topic_name)

        # TODO: Configure the AvroProducer
        self.producer = AvroProducer(
                            self.broker_properties,
                            default_key_schema = self.key_schema,
                            default_value_schema = self.value_schema
                        )

    def create_topic(self):
        """Creates the producer topic if it does not already exist"""
        #
        #
        # TODO: Write code that creates the topic for this producer if it does not already exist on
        # the Kafka Broker.
        #
        #
        
        client = AdminClient({"bootstrap.servers": BROKER_URL})
        
        # Skips if topic already exists
        topic_metadata = client.list_topics(timeout=5)
        if self.topic_name in set(t.topic for t in iter(topic_metadata.topics.values())):
            logger.info(f"{self.topic_name} already exists.")
            return
        
        futures = client.create_topics(
                        [
                            NewTopic(
                                topic=self.topic_name,
                                num_partitions=self.num_partitions,
                                replication_factor=self.num_replicas,
                                config={
                                    "cleanup.policy": "delete",
                                    "compression.type": "lz4",
                                    "delete.retention.ms": "100",
                                    "file.delete.delay.ms": "100",
                                },
                            ),

                        ]
                    )

        for topic, future in futures.items():
            try:
                future.result()
                logger.info(f"created {self.topic_name}")
            except Exception as e:
                logger.error(f"failed to create {self.topic_name}: {e}")

    def time_millis(self):
        return int(round(time.time() * 1000))

    def close(self):
        """Prepares the producer for exit by cleaning up the producer"""
        #
        #
        # TODO: Write cleanup code for the Producer here
        #
        #
        if self.producer is not None:
            logger.info("flushing producer")
            self.producer.flush()
        else:
            logger.info("producer close incomplete - skipping")

    def time_millis(self):
        """Use this function to get the key for Kafka Events"""
        return int(round(time.time() * 1000))
