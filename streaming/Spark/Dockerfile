FROM apache/spark
WORKDIR /app
USER root
RUN pip install pyspark pandas numpy elasticsearch
RUN apt update
RUN apt-get install libatlas3-base libopenblas-base -y
RUN apt upgrade -y
CMD ["/usr/local/lib/python3.8/dist-packages/pyspark/bin/spark-submit" \
,"--jars","spark-sql-kafka-0-10_2.12-3.0.0.jar,spark-streaming-kafka-0-10-assembly_2.12-3.0.0.jar,kafka-clients-0.10.2.2.jar,commons-pool2-2.8.0.jar","/app/process.py"]
