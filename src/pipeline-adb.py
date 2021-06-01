import sys
import os
import configparser

import pandas
import cx_Oracle
from sqlalchemy.types import String, Integer

config = configparser.RawConfigParser()
config.read('datastore.properties')

driver = config.get('oracle-api','database.driver')
tns = config.get('oracle-api','database.tns')
data_user = config.get('oracle-api','data.user')
data_password = config.get('oracle-api','data.password')
admin_user = config.get('oracle-api','admin.user')
admin_password = config.get('oracle-api','admin.password')

print(driver)
print(tns)
print(data_user)
print(admin_user)

if len(sys.argv) >= 2:
  command = sys.argv[1]
if len(sys.argv) >= 3:
  filename = sys.argv[2]
  base = os.path.basename(filename)
  data_name = os.path.splitext(base)[0]
  print('reading from '+data_name)

def dd_readfile(filename):
  try:
    pdf = pandas.read_csv(filename,encoding='utf-8');
    return pdf;
  except Exception as err:
    print(err);
    return pandas.DataFrame();

def store_sample():
  dd = dd_readfile(filename)
  print(dd.columns.tolist())
  sfs = {}
  for dt in dd.dtypes.index:
    print(dt,dd.dtypes[dt])
    if dd.dtypes[dt] == 'int64':
      sfs[dt] = Integer()
    else:
      sfs[dt] = String(4000)
  dd.to_sql(data_name,'oracle+cx_oracle://'+data_user+':'+data_password+'@'+tns,dtype=sfs,if_exists='replace',index=False) # the error shows here

def expose_sample():
  connection = cx_Oracle.connect(user=data_user, password=data_password, dsn=tns, encoding='UTF-8')
  cur = connection.cursor()
  stmt = """
    DECLARE
      l_priv_roles owa.vc_arr;
      l_priv_patterns owa.vc_arr;
    BEGIN
      l_priv_roles(1) := 'oracle.dbtools.role.autorest.@USER.@TABLE';
      l_priv_roles(2) := 'oracle.dbtools.autorest.any.schema';
      l_priv_roles(3) := 'SQL Developer';
      l_priv_patterns(1) := '/metadata-catalog/@URL/*';
      l_priv_patterns(2) := '/@URL/*';
      ORDS.enable_object (
        p_enabled      => TRUE, -- Default  { TRUE | FALSE }
        p_schema       => '@USER',
        p_object       => '@TABLE',
        p_object_type  => 'TABLE', -- Default  { TABLE | VIEW }
        p_object_alias => '@URL',
        p_auto_rest_auth => TRUE
      );
      ORDS.define_privilege(
        p_privilege_name     => 'oracle.dbtools.autorest.privilege.@USER.@TABLE',
        p_roles              => l_priv_roles,
        p_patterns           => l_priv_patterns,
        p_label              => 'oracle.dbtools.autorest.privilege.@USER.@TABLE',
        p_description        => 'oracle.dbtools.autorest.privilege.@USER.@TABLE'
      );
      COMMIT;
    END;
    """
  stmt = stmt.replace('@USER',data_user.upper())
  stmt = stmt.replace('@TABLE',data_name.upper())
  stmt = stmt.replace('@URL',data_name.lower())
  cur.execute(stmt)

def drop_sample():
  connection = cx_Oracle.connect(user=data_user, password=data_password, dsn=tns, encoding='UTF-8')
  cur = connection.cursor()
  stmt = """
    DROP TABLE @TABLE
    """
  stmt = stmt.replace('@TABLE',data_name.upper())
  cur.execute(stmt)
  cur = connection.cursor()
  stmt = """
    BEGIN
      ORDS.delete_privilege(
        p_name     => 'oracle.dbtools.autorest.privilege.@USER.@TABLE'
      );
      COMMIT;
    END;
    """
  stmt = stmt.replace('@USER',data_user.upper())
  stmt = stmt.replace('@TABLE',data_name.upper())
  cur.execute(stmt)

def create_infra():
  connection = None
  stmt = """
    CREATE USER @USER IDENTIFIED BY "@PASSWORD"
    """
  stmt = stmt.replace('@USER',data_user)
  stmt = stmt.replace('@PASSWORD',data_password)
  try:
    connection = cx_Oracle.connect(user=admin_user, password=admin_password, dsn=tns, encoding='UTF-8')
    cur = connection.cursor()
    cur.execute(stmt)
  except:
    print('error')
  stmt = """
    GRANT RESOURCE, CONNECT, UNLIMITED TABLESPACE TO @USER
    """
  stmt = stmt.replace('@USER',data_user)
  try:
    cur.execute(stmt)
  except:
    print('error')
  connection.close()
  stmt = """
    DECLARE
      l_priv_roles owa.vc_arr;
      l_priv_patterns owa.vc_arr;
    BEGIN
      ORDS.enable_schema(
        p_enabled             => TRUE,
        p_schema              => '@USER',
        p_url_mapping_type    => 'BASE_PATH',
        p_url_mapping_pattern => '@URL',
        p_auto_rest_auth      => TRUE
      );
      OAUTH.DELETE_CLIENT(p_name => '@USER_api');
      ORDS.CREATE_ROLE(p_role_name=>'@USER api');
      OAUTH.CREATE_CLIENT(
        p_name            => '@USER_api',
        p_grant_type      => 'client_credentials',
        p_owner           => 'Name',
        p_description     => '@USER OAuth client user',
        p_support_email   => '@URL@domain.com',
        p_privilege_names => '');
      OAUTH.GRANT_CLIENT_ROLE(
        p_client_name => '@USER_api',
        p_role_name   => '@USER api'
      );
      l_priv_roles(1) := 'oracle.dbtools.role.autorest.@USER';
      l_priv_roles(2) := '@USER api';
      l_priv_roles(3) := 'oracle.dbtools.autorest.any.schema';
      l_priv_patterns(1) := '/metadata-catalog/*';
      ords.define_privilege(
        p_privilege_name     => 'oracle.dbtools.autorest.privilege.@USER',
        p_roles              => l_priv_roles,
        p_patterns           => l_priv_patterns,
        p_label              => 'oracle.dbtools.autorest.privilege.@USER',
        p_description        => 'oracle.dbtools.autorest.privilege.@USER'
      );
      COMMIT;
    END;
    """
  stmt = stmt.replace('@USER',data_user.upper())
  stmt = stmt.replace('@URL',data_user.lower())
  try: 
    connection = cx_Oracle.connect(user=data_user, password=data_password, dsn=tns, encoding='UTF-8')
    cur = connection.cursor()
    cur.execute(stmt)
  except:
    print('error')
  finally:
    connection.close()

def drop_infra():
  connection = None
  stmt = """
    BEGIN
      ORDS.DELETE_PRIVILEGE(
        p_name     => 'oracle.dbtools.autorest.privilege.@USER'
      );
      OAUTH.REVOKE_CLIENT_ROLE(
        p_client_name => '@USER_api',
        p_role_name   => '@USER api'
      );
      OAUTH.DELETE_CLIENT(p_name => '@USER_api');
      ORDS.DELETE_ROLE(p_role_name=>'@USER api');
      ORDS.enable_schema(
        p_enabled             => FALSE,
        p_schema              => '@USER'
      );
      COMMIT;
    END;
    """
  stmt = stmt.replace('@USER',data_user.upper())
  try:
    connection = cx_Oracle.connect(user=data_user, password=data_password, dsn=tns, encoding='UTF-8')
    cur = connection.cursor()
    cur.execute(stmt)
  except:
    print('error')
  finally:
    if connection != None:
      connection.close()
  stmt = """
    DROP USER @USER CASCADE
    """
  stmt = stmt.replace('@USER',data_user.upper())
  try:
    connection = cx_Oracle.connect(user=admin_user, password=admin_password, dsn=tns, encoding='UTF-8')
    cur = connection.cursor()
    cur.execute(stmt)
  except:
    print('error')
  finally:
    if connection != None:
      connection.close()

def get_infra():
  connection = cx_Oracle.connect(user=data_user, password=data_password, dsn=tns, encoding='UTF-8')
  cur = connection.cursor()
  stmt = """
    DROP TABLE @TABLE
    """
  stmt = stmt.replace('@TABLE',data_name.upper())
  cur.execute(stmt)
  cur = connection.cursor()
  stmt = """
    BEGIN
      ORDS.delete_privilege(
        p_name     => 'oracle.dbtools.autorest.privilege.@USER.@TABLE'
      );
      COMMIT;
    END;
    """
  stmt = stmt.replace('@USER',data_user.upper())
  stmt = stmt.replace('@TABLE',data_name.upper())
  cur.execute(stmt)

if __name__ == '__main__':
  if command == 'create':
    print('creating infra')
    create_infra()
  elif command == 'get':
    print('get infra')
    get_infra()
  elif command == 'drop':
    print('dropping infra')
    drop_infra()
  elif command == 'put':
    print('putting '+data_name)
    store_sample()
    expose_sample()
  elif command == 'delete':
    print('deleting '+data_name)
    drop_sample()

  print('done')

