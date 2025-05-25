from typing import Union
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy import select
from sqlalchemy.orm import declarative_base, Session

from pyswark.gluedb import recordmodel

Base = declarative_base()


class Info( Base ):
    __tablename__ = 'Info'

    id            = Column( Integer, primary_key=True )
    index         = Column( Integer )
    name          = Column( String, nullable=False, unique=True )
    date_created  = Column( DateTime, nullable=False )
    date_modified = Column( DateTime, nullable=False )


class Body( Base ):
    __tablename__ = 'Body'

    id    = Column( Integer, primary_key=True )
    index = Column( Integer )
    model = Column( String, nullable=False )


class DbBackend:
    def __init__(self, records: list[ recordmodel.Record]):
        # Create an in-memory SQLite database
        engine = create_engine( 'sqlite:///:memory:', echo=False )

        # Create tables
        Base.metadata.create_all( engine )

        self._count = 0
        self._session = Session( engine )
        self.addRecords( records )

    def Session(self):
        return self._session

    def addRecords( self, records ):
        with self.Session() as session:
            for record in records:
                self._addRecord( session, self._count, record )
                self._count += 1
            session.commit()

    @staticmethod
    def _addRecord( session, index, record ):
        session.add( Info(
            index         = index,
            name          = record.info.name,
            date_created  = record.info.date_created.datetime,
            date_modified = record.info.date_modified.datetime,
        ))
        session.add( Body( index=index, model=record.body['model'] ))

    def addRecord( self, record ):
        self.addRecords([ record ])

    def selectInfoAndBody(self):
        query = select( Info, Body ).join( Body, Info.index == Body.index )
        with self.Session() as session:
            results = session.execute( query ).all()
        return results

    @staticmethod
    def getIndices( results: list[ Union[ Info, Body ]] ):
        return ( record.index for record in results )

    def delete( self, query ):
        """ delete a record based on query """
        with self.Session() as session:
            results = self._delete( session, query )
            if results:
                session.commit()
        return results

    def _delete( self, session, query ):
        results = session.execute( query ).scalars().all()
        for result in results:
            session.delete( result )
            self._decrement( session, results )

        return results

    def _decrement( self, session, results ):
        for result in results:
            self._count -= 1
            self._decrementTable( session, result, Table=Info )
            self._decrementTable( session, result, Table=Body )

    def _decrementTable( self, session, result, Table ):
        query   = select( Table ).where( Table.index > result.index )
        results = session.execute( query ).scalars().all()
        for r in results:
            r.index -= 1
        return results
