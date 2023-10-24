FROM logstash:8.10.4
FROM polygon_test
WORKDIR /app
COPY logstash.conf /app
RUN cp 
CMD ["bin/logstash", "-f", "/input-json.conf"]