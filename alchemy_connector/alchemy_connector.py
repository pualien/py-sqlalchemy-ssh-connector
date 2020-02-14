import paramiko
import yaml
import pandas as pd

from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine


class ConnectDisconnectSSHTunnelForwarder(SSHTunnelForwarder):
    def __init__(self, connector, *args, **kwargs):
        self.connector = connector
        super().__init__(*args, **kwargs)

    def __enter__(self):
        # enters SSHTunnelForwarder context manager
        super().__enter__()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        # close SQLAlchemy connection and resets server
        self.connector.disconnect()
        # exit SSHTunnelForwarder context manager
        super().__exit__()


class AlchemyConnector:
    def __init__(self, stage_environment, yaml_path, use_ssh=True, keep_open=False):
        # open yaml file
        with open(yaml_path) as f:
            # load yaml file based on stage environment
            self.data_map = yaml.safe_load(f)[stage_environment]
            self.connection = None
            self.db_url = None
            self.server = None
            self.use_ssh = use_ssh
            self.keep_open = keep_open

    def init_ssh(self):
        """
        initiate ConnectDisconnectSSHTunnelForwarder context manager
        :return: ConnectDisconnectSSHTunnelForwarder context manager
        """
        mypkey = paramiko.RSAKey.from_private_key_file(self.data_map["ssh_host_key"])
        self.server = ConnectDisconnectSSHTunnelForwarder(self,
            (self.data_map["ssh_host"], 22),
            ssh_username=self.data_map["ssh_username"],
            ssh_pkey=mypkey,
            remote_bind_address=(self.data_map["host"], self.data_map["port"])
        )
        self.server.daemon_forward_servers = True
        return self.server

    def connect(self):
        """
        opens SQLAlchemy connection
        :return: SQLAlchemy connection
        """
        if self.connection is None and self.use_ssh:
            self.db_url = "{adapter}://{username}:{password}@localhost:{local_bind_port}/{database}".format(**self.data_map, local_bind_host=self.server.local_bind_host, local_bind_port=self.server.local_bind_port)
        else:
            self.db_url = "{adapter}://{username}:{password}@{host}:{port}/{database}".format(**self.data_map)

        self.connection = create_engine(self.db_url).connect()
        return self.connection

    def disconnect(self):
        """
        close SQLAlchemy connection
        :return:
        """
        if self.connection:
            if not self.connection.closed:
                self.connection.close()
            self.connection = None
        self.server = None

    def execute(self, query):
        """
        execute query
        :param query: SQL query
        :return: list of dict of query results
        """
        if self.use_ssh:
            self.init_ssh()
            with self.server:
                result_proxy = self.connect().execute(query)
        result = [{column: value for column, value in rowproxy.items()} for rowproxy in result_proxy]
        return result

    def pd_execute(self, query):
        """
        execute query
        :param query: SQL query
        :return: pandas DataFrame of query results
        """
        if self.use_ssh:
            self.init_ssh()
            with self.server:
                df = pd.read_sql_query(query, self.connect())
        else:
            df = pd.read_sql_query(query, self.connect())
            self.disconnect()
        return df

