from pyswark.lib.aenum import AliasEnum, Alias


class Guitarists( AliasEnum ):

    # Bands that start with 'the':
    THE_ALLMAN_BROTHERS_BAND = 'Duane Allman', Alias( 'The Allman Brothers' )
    THE_GRATEFUL_DEAD        = 'Jerry Garcia', Alias( 'The Dead', 'The Grateful Dead' )

    # Bands with special charaters
    AC_DC        = 'Angus Young', Alias( 'AC/DC' )
    GUNS_N_ROSES = 'Slash', Alias( "Guns N' Roses" )


def baseEnumBehavior():
    # base enum getattr behavior
    guitarist = Guitarists.THE_GRATEFUL_DEAD
    print( guitarist.value ) # 'Jerry Garcia'

def patchedBehavior():
    # patched method .get()
    guitarists = [
        Guitarists.get( Guitarists.THE_GRATEFUL_DEAD ), # via enum
        Guitarists.get( 'THE_GRATEFUL_DEAD' ),          # via enum name
        Guitarists.get( 'The Dead' ),                   # via alias 0
        Guitarists.get( 'The Grateful Dead' ),          # via alias 1
    ]

    assert all( g.value == 'Jerry Garcia' for g in guitarists )
