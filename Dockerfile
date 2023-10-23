FROM alpine
RUN apk update && apk add php composer vim php-fileinfo
WORKDIR /app
COPY . /app
RUN composer require polygon-io/api -W
CMD ["php" "polygon.php"]

