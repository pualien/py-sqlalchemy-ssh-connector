





from alchemy_connector import SQLAlchemySession



session = SQLAlchemySession(
    host='db.example.com',
    port='21',
    user='myuser',
 key='/home/myplace/.ssh/id_rsa',
    to_port='37017',
    to_host='0.0.0.0'
)



df = session.pd_execute('''select * 
from ecommerce_transactions 
limit 1''')


...

session.stop()

