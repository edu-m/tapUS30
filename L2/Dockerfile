FROM logstash:8.10.4
FROM polygon_test
WORKDIR /app
COPY logstash.conf /app
CMD ["bin/logstash", "-f", "/input-json.conf"]