





import pandas as pd
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder


server = SSHTunnelForwarder(
    'myuser',
    ssh_username='myuser',
    ssh_pkey='/home/myplace/.ssh/id_rsa',
    remote_bind_address=('0.0.0.0',
                         '37017')
)



server.start()


adapter = 'mysql+pymysql'
db_url = 'mysql+pymysql://myuser@localhost:{local_bind_port}'\
    .format(local_bind_port=server.local_bind_port)



engine = create_engine(db_url)



connection = engine.connect()



df = pd.read_sql_query('''
select * 
from ecommerce_transactions 
limit 1
''', connection)


...

connection.close()



server.stop()
