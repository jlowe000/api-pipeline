import sys
import os
import configparser

import mimetypes
import oci

config = configparser.RawConfigParser()
config.read('datastore.properties')

bucketname = config.get('oracle-api','oci.bucketname')
profile = config.get('oracle-api','oci.profile')
config = config.get('oracle-api','oci.config')

print(profile)
print(bucketname)

command = sys.argv[1]
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
    response = os.put_object(namespace,bucketname,filename,f,content_type=mimetype)
    print(response)

def delete_sample():
  ociconfig = oci.config.from_file(config,profile)
  os = oci.object_storage.ObjectStorageClient(ociconfig)
  namespace = os.get_namespace().data
  print(namespace)
  response = os.delete_object(namespace,bucketname,filename)
  print(response)

if __name__ == '__main__':
  if command == 'put':
    print('loading '+data_name)
    upload_sample()
  elif command == 'delete':
    print('deleting '+data_name)
    delete_sample()

  print('done')
