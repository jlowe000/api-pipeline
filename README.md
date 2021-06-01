# api-pipeline

## Purpose

- To simplify the ability to create / upload datasets into Autonomous Database

## Principles

- Locally executed
- As little infrastructure required
- Command line driven (initially)

## Steps To Run

- Download this repo
- Create ADB instance in OCI
- Download ADB wallet, unzip wallet and configure wallet (ie sqlnet.ora)
- Download Oracle Instant Client and unzip
- set environment variables
  - TNS_ADMIN to the location of the wallet
  - LD_LIBRARY_PATH (on linux) and PATH (on Windows) to the location of the Oracle Instant Client
- Install python requirements (using pip3 install -r requirements.txt)
- Using datastore.properties.template (and copying it to datastore.properties), set parameters
  - TNS name to use
  - Username / Password for admin user (from Autonomous Database configuration)
  - Username / Password for datastore user (to be configured)
  - OCI configuration (optional for Object Storage extension)
  
## Samples Executions

To create the schema user and enable Oracle REST Data Services (ORDS)
```
$ python3 src/pipeline-bootstrap.py create
```
To upload a CSV, create table, load the data and enable a REST interface
```
$ python3 src/pipeline-adb.py put data/sample.csv
```
To disable a REST interface and drop the table
```
$ python3 src/pipeline-adb.py delete data/sample.csv
```
To disable Oracle REST Data Services (ORDS) and drop the schema user
```
$ python3 src/pipeline-bootstrap.py drop
```
