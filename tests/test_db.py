from yo import config
from yo import db
from unittest import mock
from sqlalchemy import select
from sqlalchemy import MetaData
from sqlalchemy import func

def test_empty_sqlite():
    """Test we can get a simple empty sqlite database"""
    yo_config = config.YoConfigManager(None,defaults={'database':{'provider'   :'sqlite',
                                                                  'init_schema':'0'},
                                                      'sqlite':{'filename':':memory:'}})
    yo_db = db.YoDatabase(yo_config)
    assert len(yo_db.engine.table_names())==0

def test_schema_sqlite():
    """Test init_schema creates empty tables"""
    yo_config = config.YoConfigManager(None,defaults={'database':{'provider'   :'sqlite',
                                                                  'init_schema':'1'},
                                                      'sqlite':{'filename':':memory:'}})
    yo_db = db.YoDatabase(yo_config)
    assert len(yo_db.engine.table_names()) >0
    m = MetaData()
    m.reflect(bind=yo_db.engine)
    for table in m.tables.values():
        with yo_db.acquire_conn() as conn:
             query    = table.select().where(True)
             response = conn.execute(query).fetchall()
             assert len(response)==0

def test_initdata_param():
    """Test we can pass initdata in from the kwarg"""
    yo_config = config.YoConfigManager(None,defaults={'database':{'provider'   :'sqlite',
                                                                  'init_schema':'1'},
                                                      'sqlite':{'filename':':memory:'}})
    test_initdata = [["user_transports_table", {"username": "testuser", "transport_type": "email", "notify_type": "vote", "sub_data": "test@example.com"}]]
    yo_db = db.YoDatabase(yo_config,initdata=test_initdata)
    results = yo_db.get_user_transports('testuser')
    row_dict = dict(results.fetchone().items())
    for k,v in test_initdata[0][1].items():
        assert row_dict[k]==v
    assert results.fetchone() == None
