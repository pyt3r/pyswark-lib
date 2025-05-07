from typing import Union
import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import declarative_base, Session

from pyswark.gluedb import recordmodel

Base = declarative_base()

# sql operators
select = sqlalchemy.select


class Info( Base ):
    __tablename__ = 'info'

    id            = Column( Integer, primary_key=True )
    name          = Column( String, nullable=False )
    date_created  = Column( DateTime, nullable=False )
    date_modified = Column( DateTime, nullable=False )


class Body( Base ):
    __tablename__ = 'records'

    id    = Column( Integer, primary_key=True )
    model = Column( String, nullable=False )


class DbBackend:
    def __init__(self, records: list[ recordmodel.Record]):
        # Create an in-memory SQLite database
        engine = create_engine( 'sqlite:///:memory:', echo=False )

        # Create tables
        Base.metadata.create_all( engine )

        self._session = Session( engine )
        self.addRecords( records )

    def Session(self):
        return self._session

    def addRecords( self, records ):
        with self.Session() as session:
            for record in records:
                session.add( Info(
                    name          = record.info.name,
                    date_created  = record.info.date_created.datetime,
                    date_modified = record.info.date_modified.datetime,
                ))
                session.add( Body( model=record.body['model'] ))
            session.commit()

    def addRecord( self, record ):
        self.addRecords([ record ])

    @staticmethod
    def getIndices( results: list[ Union[ Info, Body ]] ):
        return ( record.id - 1 for record in results )

    def runQuery( self, query ):
        with self.Session() as session:
            records = session.execute( query ).scalars().all()
        return records
