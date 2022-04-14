from sqlalchemy import create_engine, MetaData, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

engine = create_engine(r'sqlite:///' + os.path.join(os.getcwd(), 'database', 'database.sqlite'))
Session = sessionmaker(bind=engine)

def add_column(engine, table_name, column):
    column_name = column.compile(dialect=engine.dialect)
    column_type = column.type.compile(engine.dialect)
    engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))


# add_column(engine, "users", Column("state", String(100), primary_key=True))

Base = declarative_base()

