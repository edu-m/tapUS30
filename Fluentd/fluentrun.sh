docker run -ti -m 6000m --cpus=6 --rm -v "$PWD":/fluentd/etc fluentd -c /fluentd/etc/fluent.conf 
