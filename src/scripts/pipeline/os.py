import sys
import os
import configparser

import mimetypes
import oci

config = configparser.RawConfigParser()
config.read('datastore.properties')

bucket_name = config.get('oracle-api','oci.bucket.name')
bucket_compartment_ocid = config.get('oracle-api','oci.bucket.compartment')
profile = config.get('oracle-api','oci.profile')
config = config.get('oracle-api','oci.config')

print(profile)
print(bucket_name)
print(bucket_compartment_ocid)

if len(sys.argv) >= 2:
  command = sys.argv[1]
if len(sys.argv) >= 3:
  filename = sys.argv[2]
  base = os.path.basename(filename)
  data_name = os.path.splitext(base)[0]
  print('reading from '+data_name)

def upload_sample():
  ociconfig = oci.config.from_file(config,profile)
  os = oci.object_storage.ObjectStorageClient(ociconfig)
  namespace = os.get_namespace().data
  print(namespace)
  # Override Javascript types
  mimetype = mimetypes.guess_type(filename)[0]
  print(filename)
  print(mimetype)
  with open(filename, 'rb') as f:
    response = os.put_object(namespace,bucket_name,filename,f,content_type=mimetype)
    print(response)

def delete_sample():
  ociconfig = oci.config.from_file(config,profile)
  os = oci.object_storage.ObjectStorageClient(ociconfig)
  namespace = os.get_namespace().data
  print(namespace)
  response = os.delete_object(namespace,bucket_name,filename)
  print(response)

def create_bucket():
  global bucket_compartment_ocid
  ociconfig = oci.config.from_file(config,profile)
  if bucket_compartment_ocid == None or bucket_compartment_ocid == '':
    bucket_compartment_ocid = ociconfig['tenancy']
  os = oci.object_storage.ObjectStorageClient(ociconfig)
  namespace = os.get_namespace().data
  details = oci.object_storage.models.CreateBucketDetails(name=bucket_name,compartment_id=bucket_compartment_ocid,public_access_type='ObjectRead',storage_tier='Standard')
  response = os.create_bucket(namespace,details)

def drop_bucket():
  ociconfig = oci.config.from_file(config,profile)
  os = oci.object_storage.ObjectStorageClient(ociconfig)
  namespace = os.get_namespace().data
  response = os.delete_bucket(namespace,bucket_name)

if __name__ == '__main__':
  if command == 'create':
    print('creating '+bucket_name)
    create_bucket()
  elif command == 'drop':
    print('dropping '+bucket_name)
    drop_bucket()
  elif command == 'put':
    print('loading '+data_name)
    upload_sample()
  elif command == 'delete':
    print('deleting '+data_name)
    delete_sample()

  print('done')
