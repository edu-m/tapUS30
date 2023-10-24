<?php
require __DIR__ . '/vendor/autoload.php';
use PolygonIO\Rest\Rest;

$api_key = 'WMHNmBNvAx5V3IdOqMzFlytWyDq3jlln';
$tickers = array(
    "AXP",
    "AMGN",
    "AAPL",
    "BA",
    "CAT",
    "CSCO",
    "CVX",
    "GS",
    "HD",
    "HON",
    "IBM",
    "INTC",
    "JNJ",
    "KO",
    "JPM",
    "MCD",
    "MMM",
    "MRK",
    "MSFT",
    "NKE",
    "PG",
    "TRV",
    "UNH",
    "CRM",
    "VZ",
    "V",
    "WBA",
    "WMT",
    "DIS",
    "DOW"
);

$currentDate = new DateTime();
$startingDate = new DateTime();
$interval = new DateInterval('P2Y1D');
$startingDate->sub($interval);

$rest = new Rest($api_key);

foreach($tickers as $ticker){
    sleep(12);
    $file = fopen("data/raw/$ticker".".json","w") or die("Unable to open file !");
    $data = json_encode($rest->stocks->aggregates->get(
        $ticker,
        1,
        $startingDate->format('Y-m-d'),
        $currentDate->format('Y-m-d'),
        'day'
    ));
    fwrite($file, $data);
    fclose($file);
}
