FROM apache/spark
WORKDIR /app
#COPY process.py .
USER root
RUN pip install pyspark pandas numpy
RUN apt update
RUN apt-get install libatlas3-base libopenblas-base -y
RUN apt upgrade -y
# RUN update-alternatives --config libblas.so.3
CMD ["/usr/local/lib/python3.8/dist-packages/pyspark/bin/spark-submit","/app/process.py"]
#CMD ["/bin/bash"]
