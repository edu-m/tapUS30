FROM apache/spark
WORKDIR /app
#COPY process.py .
USER root
RUN pip install pyspark pandas
CMD ["/usr/local/lib/python3.8/dist-packages/pyspark/bin/spark-submit" \
,"--packages","org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0","/app/process.py"]