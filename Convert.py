import pandas as pd
import os
import argparse
import hashlib
import mysql.connector
from sqlalchemy import create_engine

mysql_username = "root"
mysql_password = os.environ.get('MYSQL_PASSWORD')
mysql_host = "localhost"
mysql_port = 3306
chunksize = 10000


def compare_hashes(password):
    if hashlib.sha512(password.encode()).hexdigest() == mysql_password:
       return password


def connect_to_mysql(password, database):
    return mysql.connector.connect(
        user=mysql_username,
        password=compare_hashes(password),
        host=mysql_host,
        port=mysql_port,
        database=database
    )

def DataframeValue(df, columns, value):
    if df[columns].dtype == 'str' or df[columns].dtype == 'object':
        if df[columns].str.contains(value).any():
            return True
    return False

def get_sql_data_type(python_type):
    sql_data_types = {
        'int64': 'BIGINT',
        'int':'INT',
        'float':'FLOAT',
        'float64': 'DOUBLE',
        'string': 'VARCHAR(50)',
        'datetime64[ns]': 'DATETIME',
    }
    return sql_data_types.get(python_type, 'VARCHAR(50)')

def Regex(pattern, series):
    return series.astype(str).str.match(pattern).all()

def df_to_sql(dataframe, table_name, connection, username, password, host, port, database):
    engine = create_engine(f'mysql+mysqlconnector://{username}:{compare_hashes(password)}@{host}:{port}/{database}')
    connection = engine.raw_connection()
    cursor = connection.cursor()
    columns = ','.join([f'{col} {get_sql_data_type(dataframe[col].dtype)}' for col in dataframe.columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
    dataframe.to_sql(name=table_name, con=engine, if_exists='replace', chunksize=chunksize, index=False)
    connection.commit()
    connection.close()

         
def Filter(df, columns):        
    if DataframeValue(df, columns, '.'):
        try:
            df[columns] = df[columns].astype('int')
        except ValueError:
            print("Error converting '{}' column to {}".format(columns, df[columns].dtype))
    if DataframeValue(df, columns, '€') or DataframeValue(df, columns, ','):
        try:
            df[columns] = df[columns].replace({',': '.', '€': ''}, regex=True).astype('float')
        except ValueError:
            print("Error converting '{}' column to {}".format(columns, df[columns].dtype))
    if DataframeValue(df, columns, '-') and Regex(r'^\d\d\d\d-\d\d-\d\d$', df[columns].head(1)) or Regex(r'^\d\d-\d\d-\d\d\d\d$', df[columns].head(1)):
        try:
            df[columns] = pd.to_datetime(df[columns])
        except ValueError:
            print("Error converting '{}' column to {}".format(columns, df[columns].dtype))
    if Regex(r'^\d\d:\d\d$', df[columns].head(1)):
        try:
            df[columns] = pd.to_datetime(df[columns])
            df[columns] = df[columns].dt.hour * 3600 + df[columns].dt.minute * 60
            df[columns] = df[columns].astype(int)
        except ValueError:
            print("Error converting '{}' column to {}".format(columns, df[columns].dtype))
    if Regex(r'^[a-zA-Z]+(?:\d)?$', df[columns].head(1)):
        try:
            df[columns] = df[columns].astype('string')
        except ValueError:
            print("Error converting '{}' column to {}".format(columns, df[columns].dtype))
    return df

                        



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converter CSV File to SQL Entity')
    parser.add_argument('-f', '-file', type=str, dest='file', required=True, help='Select name file without extension file')
    parser.add_argument('-p', '-password', type=str, dest='password', required=True, help='Select name file without extension file')
    parser.add_argument('-path', '-path', type=str, dest='path', required=True, help='Select name file without extension file')
    parser.add_argument('-t', '-table', type=str, dest='table', required=True, help='Select name file without extension file')
    args = parser.parse_args()
    path = os.listdir(args.path)
    filtered_df = None
    connection = connect_to_mysql(args.password, args.file)
    if len(path) > 0:
        for files in path:
            if str(args.file.capitalize() + '.csv') == files or str(args.file.capitalize() + '.csv').lower() == files:
                df = pd.read_csv(os.path.join(args.path, files),low_memory=False)
                if 'Unnamed: 0' in df.columns:
                    df = df.drop(columns='Unnamed: 0', axis=1)
                elif df.isnull.all().all() or df.isna.all().all():
                    df = df.drop(columns=columns, axis=0)
                for columns in df.columns:
                    filtered_df = Filter(df, columns)
            else:
                print('No file found !')
                print(files)
        print(filtered_df.loc[filtered_df.value_counts().head(10)])
        df_to_sql(filtered_df,args.table,connection,mysql_username,args.password,mysql_host,mysql_port,args.file)
        print("Process finished")