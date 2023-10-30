FROM docker.elastic.co/logstash/logstash:8.10.4
RUN rm -f /usr/share/logstash/pipeline/logstash.conf
COPY logstash.conf /usr/share/logstash/pipeline/logstash.conf
COPY raw/ /tmp
#CMD ["cat", "/usr/share/logstash/pipeline/logstash.conf"]
CMD ["/usr/share/logstash/bin/logstash", "-f", "/usr/share/logstash/pipeline"]