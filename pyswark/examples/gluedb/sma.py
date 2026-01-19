""" used in the gluedb blog post: https://pyt3r.github.io/ """

def main():

    # connect to a db
    from pyswark.core.io import api as io_api
    from pyswark.gluedb import api
    
    db = io_api.read( 'pyswark:/data/sma-example.gluedb', datahandler='pjson' )

    # view the names
    print( db.getNames() )

    # get the record
    record = db.get( 'JPM' )
    print( record.body )

    # acquire the model
    contents = record.acquire()
    print( type(contents) )

    # extract the data
    JPM = contents.extract()
    print( JPM.head(2) )

    # extract the data via string
    JPM = db.extract( "JPM" )

    # extract the data via enum
    Enum = db.enum
    JPM  = db.extract( Enum.JPM.value )

    # get records by query
    from sqlmodel import Session, select

    sqlDb = db.asSQLModel() # convert gluedb to sqlmodel

    with Session( sqlDb.engine ) as session:

        recordsBefore2026 = session.exec( 
            select( sqlDb.RECORD )
            .where( 
                sqlDb.INFO.date_created < '2026-01-01' 
            )
        ).all()

        recordsAfter2026 = session.exec( 
            select( sqlDb.RECORD )
            .where( 
                sqlDb.INFO.date_created >= '2026-01-01' 
            )
        ).all()

        print([ r.asModel().info.name for r in recordsBefore2026 ])
        # ['JPM', 'BAC']
        print([ r.asModel().info.name for r in recordsAfter2026 ])
        # ['kwargs']

    # == create a new db ==
    from pyswark.gluedb import api
    from pyswark.core.models import collection, primitive

    db = api.newDb()
    db.post( 'pyswark:/data/ohlc-jpm.csv.gz', name='JPM' )
    db.post( 'pyswark:/data/ohlc-bac.csv.gz', name='BAC' )
    db.post( primitive.Int("60.0"), name='window' )
    db.post( collection.Dict({ "window": 60 }), name='kwargs' )
    db.delete( 'window' )

    from pyswark.core.io.api import write
    write( db, 'file:./sma-example.gluedb' ) if False else None


    # == analytics workflow ==
    from pyswark.gluedb import api

    db = api.connect( 'pyswark:/data/sma-example.gluedb' )

    # extract the data
    Enum   = db.enum
    JPM    = db.extract( Enum.JPM.value )
    BAC    = db.extract( Enum.BAC.value )
    kwargs = db.extract( Enum.kwargs.value )

    # Calculate the simple moving average (SMA)
    JPM_SMA = JPM.rolling( **kwargs ).mean()
    BAC_SMA = BAC.rolling( **kwargs ).mean()

    dashboard = plotSMAs(JPM_SMA, BAC_SMA, kwargs)


def plotSMAs(JPM_SMA, BAC_SMA, kwargs):
    """ """
    import holoviews as hv
    import panel as pn

    # Clean for plotting
    JPM_SMA.index = JPM_SMA.index.astype( 'datetime64[s]' )
    BAC_SMA.index = BAC_SMA.index.astype( 'datetime64[s]' )


    # Enable notebook extension
    hv.extension('bokeh')

    # Create line plots for closing prices using index
    opts ={ 'tools': ['hover'], }
    label = lambda ticker, kwargs: f'{ticker}(window={kwargs["window"]})'
    plotJPM = hv.Curve(JPM_SMA['Close'], label=label('JPM', kwargs)).opts( **opts )
    plotBAC = hv.Curve(BAC_SMA['Close'], label=label('BAC', kwargs)).opts( **opts )

    # Combine the plots
    combined_plot = plotJPM * plotBAC

    # Style the plot
    combined_plot.opts(
        width=800,
        height=400,
        title='JPM vs BAC Price SMA',
        xlabel='Date',
        ylabel='Price ($)',
        legend_position='top_right',
        show_grid=True,
    )

    # Convert to Panel object and show
    pn.extension()
    dashboard = pn.Column(
        #pn.pane.Markdown('# JPM vs BAC Stock Price Comparison'),
        combined_plot
    )

    return dashboard

