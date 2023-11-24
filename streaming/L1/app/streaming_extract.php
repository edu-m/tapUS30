<?php
require __DIR__ . '/vendor/autoload.php';
use PhpKafka\PhpKafkaAdmin;
use PolygonIO\Rest\Rest;

$api_key = 'WMHNmBNvAx5V3IdOqMzFlytWyDq3jlln';
$tickers = array(
    "CVX" => "energy",
    "AXP" => "financial",
    "AMGN" => "health",
    "AAPL" => "tech",
    "BA" => "industrial",
    "CAT" => "industrial",
    "CSCO" => "tech",
    "GS" => "financial",
    "HD" => "cgoods",
    "HON" => "tech",
    "IBM" => "tech",
    "INTC" => "tech",
    "JNJ" => "health",
    "KO" => "cgoods",
    "JPM" => "financial",
    "MCD" => "cgoods",
    "MMM" => "industrial",
    "MRK" => "health",
    "MSFT" => "tech",
    "NKE" => "cgoods",
    "PG" => "health",
    "TRV" => "financial",
    "UNH" => "health",
    "CRM" => "tech",
    "VZ" => "tech",
    "V" => "financial",
    "WBA" => "health",
    "WMT" => "cgoods",
    "DIS" => "industrial",
    "DOW" => "industrial"
);

$currentDate = new DateTime();
$startingDate = new DateTime();
$interval = new DateInterval('P2D');
$startingDate->sub($interval);

$rest = new Rest($api_key);

function write_batch($data_array, $ticker, $category, $tickers)
{
    $path = "/data/raw/$category";
    $filename = "$ticker.txt";
    if (!file_exists($path))
        mkdir($path);
    $file = fopen($path . "/" . $filename, "w") or die("Unable to open file !");
    $results = $data_array["results"];
    foreach ($results as $result) {
        usleep(250000);
        $result["tickerSymbol"] = $ticker;
        fwrite($file, json_encode($result) . "\n");
    }
    fclose($file);
}

while (true) {
    foreach ($tickers as $ticker => $category) {
        $data = $rest->stocks->aggregates->get(
            $ticker,
            15,
            $startingDate->format('Y-m-d'),
            $currentDate->format('Y-m-d'),
            'minute'
        );
        sleep(1);
        // var_dump($data);
        write_batch($data, $ticker, $category, $tickers);
    }
    sleep(60*15);
}