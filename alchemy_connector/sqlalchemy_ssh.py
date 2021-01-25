import getpass
import pandas as pd
from urllib import parse
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from sshtunnel import SSHTunnelForwarder


class SQLAlchemySession:

    def __init__(self, host=None, user=None, password=None, key=None, uri=None, port=22, to_host='127.0.0.1',
                 to_port=3306,
                 data_map=None, local_bind_address_port=None):
        if data_map is None:
            data_map = {}
        self.data_map = data_map
        host = (data_map.get("ssh_host"), port) if data_map.get("ssh_host") else (host, port)
        user = data_map.get("ssh_username") or user or getpass.getuser()
        key = data_map.get("ssh_host_key") or key or '/home/{user}/.ssh/id_rsa'.format(user=user)
        self.to_host = to_host
        self.uri = parse.urlparse(uri)
        self.engine = None
        self.connection = None
        self.db_url = None
        self.local_bind_address_port = local_bind_address_port

        if uri:
            to_host = self.uri.hostname or to_host
            to_port = self.uri.port or to_port

        if password:
            self.server = SSHTunnelForwarder(
                host,
                ssh_username=user,
                ssh_password=password,
                remote_bind_address=(to_host, to_port)
            )
        else:
            self.server = SSHTunnelForwarder(
                host,
                ssh_username=user,
                ssh_pkey=key,
                remote_bind_address=(to_host, to_port)
            )

        if self.local_bind_address_port is not None:
            self.server.local_bind_address_port = self.local_bind_address_port

        self.start()

    def start(self):
        self.server.start()

        params = dict()

        if self.uri:

            if '@' in self.uri.netloc:
                user_pass = self.uri.netloc.split('@', 1)[0]
                if ':' in user_pass:
                    params['username'], params['password'] = user_pass.split(':', 1)
                else:
                    params['username'] = user_pass

            if self.uri.query:
                auth_mech = parse.parse_qs(self.uri.query)
                params.update({key: auth_mech[key][0] for key in auth_mech})

        self.db_url = "{adapter}://{username}:{password}@localhost:{local_bind_port}/{database}".format(
            **self.data_map, local_bind_host=self.server.local_bind_host,
            local_bind_port=self.server.local_bind_port)
        self.engine = create_engine(self.db_url, poolclass=NullPool)

        self.connection = self.engine.connect()

    def stop(self):
        self.connection.close()
        self.server.stop(force=True)
        self.connection = None
        del self.connection
        self.server = None

    def close(self):
        self.stop()

    def execute(self, query):
        """
        execute query
        :param query: SQL query
        :return: list of dict of query results
        """
        result_proxy = self.connection.execute(query)
        result = [{column: value for column, value in rowproxy.items()} for rowproxy in result_proxy]
        return result

    def pd_execute(self, query):
        """
        execute query
        :param query: SQL query
        :return: pandas DataFrame of query results
        """
        df = pd.read_sql_query(query, self.connection)
        return df
