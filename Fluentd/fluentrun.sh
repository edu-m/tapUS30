docker run -ti -m 6000m --cpus=6 --rm -v "$PWD":/fluentd/etc fluentkafka -c /fluentd/etc/fluent.conf 
