# tapUS30
Progetto di Technologies for Advanced Programming

# Progetto
Il progetto ha come scopo l'acquisizione di dati tramite API Rest di dati finanziari (aziende costituenti l'indice industriale americano "Dow Jones", anche conosciuto come "US30 Industrial Index") , che, dopo un'analisi saranno visualizzati assieme alle relative previsioni

# Funzionamento
Il progetto si compone di sei parti comunicanti e concatenate, dalla Data Ingestion alla Data Visualization passando per il Data Processing tramite Machine Learning
In particolare, il progetto presenta un modello duale batch-streaming, l'uno propedeutico all'altro; le componenti sono:
- Batch
  - Client PHP (Acquisizione Dati tramite API Polygon.io)
  - Ingestion tramite Fluentd
  - Smistamento tramite Kafka
  - Data Processing con Spark MLIB
  - Filtraggio con ElasticSearch
  - Visualizzazione tramite Kibana
 
- Streaming (todo)

La documentazione è fornita tramite notebok jupyter.
