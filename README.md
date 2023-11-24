# tapUS30
Progetto di Technologies for Advanced Programming

La documentazione completa è fornita tramite notebok jupyter.

# Progetto
Il progetto ha come scopo l'acquisizione di dati tramite Rest API (Acquisizione Dati tramite API Polygon.io) di dati finanziari delle aziende costituenti l'indice industriale americano "US30 Industrial Index", anche conosciuto come "Dow Jones". Tali dati, dopo una analisi (Data Processing + ML) saranno visualizzati assieme alle relative previsioni. Si intende dunque creare un sistema autosufficiente di consumo di dati bifase, la cui iniziale procedura batch compone i dati storici e di previsione in dei file appositi con ciascuna riga rappresentante l'andamento giornaliero per ciascuna azienda, letti successivamente per la visualizzazione. La fase successiva costituisce la procedura streaming, che si occuperà di richiedere i dati recenti e relativi al giorno corrente con una granularità di 15 minuti, da visualizzare in tempo reale e sovrapposti sui dati storici e di previsione.

# Funzionamento
Il progetto si compone di diverse parti comunicanti e concatenate, dalla Data Ingestion alla Data Visualization passando per il Data Processing tramite Machine Learning
In particolare, il progetto presenta un modello duale batch-streaming, l'uno propedeutico all'altro; le componenti sono:
- Batch
  - Client PHP Batch 
  - Data Processing con Spark MLLIB
  - Visualizzazione tramite Elasticsearch/Kibana
 
- Streaming
  - Client PHP Streaming
  - Data Ingestion tramite Fluentd
  - Smistamento tramite Kafka
  - Data Processing con Spark + Kafka Integration, Structured Streaming, MLLIB 
  - Visualizzazione tramite Elasticsearch/Kibana
