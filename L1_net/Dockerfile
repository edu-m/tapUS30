FROM alpine
RUN apk update && apk add php composer php-fileinfo iputils-ping
WORKDIR /app
COPY batch_extract.php /app
RUN composer require polygon-io/api -W
EXPOSE 8000
CMD ["php", "batch_extract.php"]
