import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from . import config

engine_str = 'sqlite:///:' + config.dbf_cache

print(engine_str)
engine = sqlalchemy.create_engine(engine_str)
session = Session(engine)

# Base.metadata.tables['XXX']即为相应的表
Base = automap_base()
Base.prepare(engine, reflect=True)
# 查询操作
result = session.query(Base.classes.nqhq).all()
# insert
# item = Base.classes.users(name='lxq', password='1234')
# session.add(item)
# session.commit()
session.close()

print(result)
