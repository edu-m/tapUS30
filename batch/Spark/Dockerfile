FROM apache/spark
WORKDIR /app
#COPY process.py .
USER root
RUN pip install pyspark pandas numpy elasticsearch
RUN apt update
RUN apt-get install libatlas3-base libopenblas-base -y
RUN apt upgrade -y
CMD ["/usr/local/lib/python3.8/dist-packages/pyspark/bin/spark-submit","/app/process.py"]
