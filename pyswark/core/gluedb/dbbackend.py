from sqlalchemy import Column, Integer, String, create_engine, select
from sqlalchemy.orm import declarative_base, Session

from pyswark.core.gluedb import recordmodel

Base = declarative_base()


class Info( Base ):
    __tablename__ = 'info'

    id   = Column( Integer, primary_key=True )
    name = Column( String, nullable=False )


class Body( Base ):
    __tablename__ = 'records'

    id    = Column( Integer, primary_key=True )
    model = Column( String, nullable=False )


class DbBackend:
    def __init__( self, records: list[ recordmodel.Record ] ):
        # Create an in-memory SQLite database
        engine = create_engine( 'sqlite:///:memory:', echo=False )

        # Create tables
        Base.metadata.create_all( engine )

        self.session = Session( engine )
        self.addRecords( records )

    def addRecords( self, records ):
        with self.session as session:
            for record in records:
                session.add( Info( name=record.info.name ))
                session.add( Body( model=record.body['model'] ))
            session.commit()

    def addRecord( self, record ):
        self.addRecords([ record ])

    def getIndices( self, query ):
        records = self.runQuery( query )
        return [ record.id - 1 for record in records ]

    def runQuery( self, query ):
        with self.session as session:
            records = session.execute( query ).scalars().all()
        return records

    @property
    def select(self):
        """ alias for sqlalchemy.select """
        return select
