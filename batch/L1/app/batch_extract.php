<?php
require __DIR__ . '/vendor/autoload.php';
use PolygonIO\Rest\Rest;

$api_key = '';
$tickers = array(
    "AXP" => "financial",
    "AMGN" => "health",
    "AAPL" => "tech",
    "BA" => "industrial",
    "CAT" => "industrial",
    "CSCO" => "tech",
    "CVX" => "energy",
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
$interval = new DateInterval('P5Y');
$startingDate->sub($interval);

$rest = new Rest($api_key);

function write_batch($data_array, $ticker, $category, $tickers)
{
    $path = "/data/raw/$category";
    $filename = "$ticker.txt";
    if(!file_exists($path))
        mkdir($path);
    $file = fopen($path."/".$filename, "w") or die("Unable to open file !");
    $results = $data_array["results"];
    foreach ($results as $result) {
        $result["tickerSymbol"] = $ticker;
        fwrite($file, json_encode($result) . "\n");
    }
    fclose($file);
}

foreach ($tickers as $ticker => $category) {
    sleep(1);
    $data = $rest->stocks->aggregates->get(
        $ticker,
        1,
        $startingDate->format('Y-m-d'),
        $currentDate->format('Y-m-d'),
        'day'
    );
    write_batch($data, $ticker, $category, $tickers);
}
