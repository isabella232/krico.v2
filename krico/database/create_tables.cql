CREATE KEYSPACE IF NOT exists krico
WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': '1' };

DROP TABLE IF exists krico.classifier_instances;
DROP TYPE IF exists krico.host_aggregate;
DROP TYPE IF exists krico.flavor;

CREATE TYPE krico.host_aggregate (
  disk map<text,int>,
  ram map<text,int>,
  name text,
  configuration_id text,
  cpu map<text,int>
);

CREATE TYPE krico.flavor (
  vcups int,
  disk int,
  ram int,
  name text
);

CREATE TABLE krico.classifier_instances (
  id uuid PRIMARY KEY,
  category text,
  name text,
  parameters map<text,int>,
  host_aggregate FROZEN<host_aggregate>,
  image text,
  host text,
  instance_id text,
  load_measured map<text,float>,
  stop_time timestamp,
  flavor FROZEN<flavor>,
  start_time timestamp
);

CREATE TABLE krico.predictor_instances (
  id uuid PRIMARY KEY,
  instance_id text,
  category text,
  image text,
  requirements map<text,float>,
  parameters map<text,int>
);
