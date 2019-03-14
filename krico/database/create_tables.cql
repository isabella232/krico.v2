CREATE KEYSPACE IF NOT exists krico
WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': '1' };

DROP TABLE IF exists krico.host_aggregate;
DROP TABLE IF exists krico.image;
DROP TABLE IF exists krico.classifier_instance;
DROP TABLE IF exists krico.classifier_network;
DROP TABLE IF exists krico.sample;
DROP TABLE IF exists krico.predictor_instance;
DROP TABLE IF exists krico.predictor_network;
DROP TYPE IF exists krico.host;
DROP TYPE IF exists krico.flavor;

CREATE TYPE krico.host (
  name text,
  configuration_id text,
  cpu map<text,int>,
  ram map<text,int>,
  disk map<text,int>
);

CREATE TYPE krico.flavor (
  name text,
  vcpus int,
  ram int,
  disk int
);

CREATE TABLE krico.host_aggregate (
  configuration_id text PRIMARY KEY,
  name text,
  cpu map<text,int>,
  ram map<text,int>,
  disk map<text,int>
);

CREATE TABLE krico.image (
  image text PRIMARY KEY,
  category text
);

CREATE TABLE krico.classifier_instance (
  id uuid,
  name text,
  configuration_id text,
  category text,
  parameters map<text,double>,
  host_aggregate FROZEN<host>,
  image text,
  host text,
  instance_id text,
  resource_usage map<text,double>,
  flavor FROZEN<flavor>,
  PRIMARY KEY ((configuration_id, category), id)
);

CREATE TABLE krico.sample (
  id uuid,
  instance_id text,
  configuration_id text,
  metrics map<text,double>,
  PRIMARY KEY ((instance_id), id)
);

CREATE TABLE krico.classifier_network (
  configuration_id text PRIMARY KEY,
  model blob,
  x_maxima map<int,double>
);

CREATE TABLE krico.predictor_instance (
  id uuid PRIMARY KEY,
  instance_id text,
  category text,
  image text,
  requirements map<text,double>,
  parameters map<text,double>
);

CREATE TABLE krico.predictor_network (
  id uuid PRIMARY KEY,
  configuration_id text,
  image text,
  category text,
  model blob,
  x_maxima map<int,double>,
  y_maxima map<int,double>
);

