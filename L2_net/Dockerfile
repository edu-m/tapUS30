FROM docker.elastic.co/logstash/logstash:8.10.4
FROM source
WORKDIR /app
COPY logstash.conf /app
CMD ["bin/logstash", "-f", "/input-json.conf"]
