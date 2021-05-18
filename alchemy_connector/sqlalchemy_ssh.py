import getpass
import pandas as pd
from urllib import parse
from sqlalchemy import create_engine, exc
from sqlalchemy.pool import NullPool

from sshtunnel import SSHTunnelForwarder


class EmptyLogger:
    @staticmethod
    def info(msg):
        pass

    @staticmethod
    def warn(msg):
        pass

    @staticmethod
    def warning(msg):
        pass

    @staticmethod
    def debug(msg):
        pass

    @staticmethod
    def critical(msg):
        pass

    @staticmethod
    def error(msg):
        pass


class SQLAlchemySession:

    def __init__(self, host=None, user=None, password=None, key=None, uri=None, port=22, to_host='127.0.0.1',
                 to_port=3306,
                 data_map=None, local_bind_address_port=None, use_ssh=True, logger=None):
        if data_map is None:
            data_map = {}
        self.data_map = data_map
        host = (data_map.get("ssh_host"), port) if self.data_map.get("ssh_host") is not None else (host, port)
        user = data_map.get("ssh_username") or user or getpass.getuser()
        key = data_map.get("ssh_host_key") or key or '/home/{user}/.ssh/id_rsa'.format(user=user)
        self.to_host = to_host
        self.uri = parse.urlparse(data_map.get("connection_uri")) if self.data_map.get("connection_uri") is not None else parse.urlparse(
            uri)
        self.engine = None
        self.connection = None
        self.db_url = None
        self.local_bind_address_port = local_bind_address_port

        if self.uri:
            to_host = self.uri.hostname or to_host
            to_port = self.uri.port or to_port
        self.use_ssh = use_ssh

        if self.use_ssh:
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
            self.logger = logger if logger is not None else EmptyLogger()

    def start(self):
        self.server.start()

        self.db_url = "{adapter}://{username}:{password}@localhost:{local_bind_port}/{database}".format(
            **self.data_map, local_bind_host=self.server.local_bind_host,
            local_bind_port=self.server.local_bind_port)
        self.engine = create_engine(self.db_url, poolclass=NullPool)

        self.connection = self.engine.connect()

    def stop(self):
        if self.use_ssh:
            self.connection.close()
            self.server.stop()
            self.connection = None
            del self.connection
            self.server = None

    def close(self):
        if self.use_ssh:
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

    def pd_execute(self, query, retry_once=True):
        """
        execute query
        :param query: SQL query
        :param retry_once: if True retries query once
        :return: pandas DataFrame of query results
        """
        if retry_once:
            try:
                df = pd.read_sql_query(query, self.connection)
            except exc.OperationalError as ex:
                self.logger.info('error: '+str(ex))
                self.stop()
                self.start()
                df = pd.read_sql_query(query, self.connection)
        else:
            df = pd.read_sql_query(query, self.connection)
        return df