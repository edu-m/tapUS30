FROM bitnami/kafka
RUN rm -f /bitnami/kafka/data/.lock
COPY init.sh /opt/bitnami/scripts/kafka
COPY init /opt/bitnami/scripts/kafka
CMD ["/opt/bitnami/scripts/kafka/init"]
#CMD ["./run.sh"]
