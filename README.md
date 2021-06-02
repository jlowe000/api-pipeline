# api-pipeline

## Purpose

- To simplify the ability to create / upload datasets into Autonomous Database

## Principles

- Locally executed
- As little infrastructure required
- Command line driven (initially)

## Dependencies

Oracle Instant Client (download from web-site) - https://www.oracle.com/database/technologies/instant-client/downloads.html
Oracle Autonomous Database (ADB) Wallet (download from ADW) - https://docs.oracle.com/en/cloud/paas/autonomous-database/adbsa/connect-download-wallet.html

## Steps To Run

- Download this repo
- Create ADB instance in OCI
- Download ADB wallet, unzip wallet and configure wallet (ie sqlnet.ora)
- Download Oracle Instant Client and unzip
- set environment variables (update bin/setenv.sh | bin/setenv.cmd and source environment)
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
$ python3 src/scripts/pipeline/adb.py create
```
To upload a CSV, create table, load the data and enable a REST interface
```
$ python3 src/scripts/pipeline/adb.py put data/sample.csv
```
To disable a REST interface and drop the table
```
$ python3 src/scripts/pipeline/adb.py delete data/sample.csv
```
To disable Oracle REST Data Services (ORDS) and drop the schema user
```
$ python3 src/scripts/pipeline/adb.py drop
```
To upload a CSV, upload the data to object storage
```
$ python3 src/scripts/pipeline/os.py put data/sample.csv
```
To delete data from object storage
```
$ python3 src/scripts/pipeline/os.py delete data/sample.csv
```

## DJango Framework

- Added an app called apiadmin
- calls the same methods in the script

To start app (from the root of the repo)
```
. ./bin/setenv.sh
python3 src/apiadmin/manage.py runserver
```
To upload a CSV file (and name the table)
```
http://localhost:8000/upload/
```
To drop table
```
http://localhost:8000/delete/
```
