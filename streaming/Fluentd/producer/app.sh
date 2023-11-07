#!/bin/sh
while true
do
	echo "Writing log to a file"
	echo '{"app":"file-myapp"}' >> /data/example-log.log
	sleep 5
done 
