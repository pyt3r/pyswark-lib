from pyswark.lib.pydantic import base
from pyswark.core.io import api as io


class Runner( base.BaseModel ):
    """Assembles and runs a workflow with a dynamically resolved state."""

    workflow : str
    state    : str

    def run( self, data_uri ):
        create_workflow = io.read( self.workflow )
        create_state    = io.read( self.state )
        return create_workflow().run( create_state( data_uri ) )
