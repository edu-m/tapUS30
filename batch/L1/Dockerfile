FROM alpine
RUN apk update && apk add php composer php-fileinfo
WORKDIR /app
COPY app/batch_extract.php /app
RUN composer require polygon-io/api -W
CMD ["php", "batch_extract.php"]
