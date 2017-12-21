import sqlalchemy
from sqlalchemy.orm import Session
from . import config


class SessionManager:

    def __init__(self):
        self.session = None

    def get_session(self):
        if self.session is None:
            engine_str = 'sqlite:///' + config.dbf_cache
            engine = sqlalchemy.create_engine(engine_str,
                                              connect_args={'check_same_thread': False})
            self.session = Session(engine)
            return self.session
        else:
            return self.session
