#!/bin/bash
kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic tech --replication-factor 1 --partitions 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic cgoods --replication-factor 1 --partitions 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic energy --replication-factor 1 --partitions 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic financial --replication-factor 1 --partitions 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic health --replication-factor 1 --partitions 1
kafka-topics.sh --bootstrap-server localhost:9092 --create --if-not-exists --topic industrial --replication-factor 1 --partitions 1
