import json
from typing import List
from pydantic import BaseModel, Field
from pyswark.lib.pydantic import ser_des


class Character( BaseModel ):
    first: str
    last: str
    role: str

    def printInfo(self):
        print( f"{ self.first } { self.last } plays the role of { self.role }." )


class TvShow( BaseModel ):
    title: str
    genre: str
    seasons: int
    characters: List[ Character ] = Field( default_factory=list )

    def printInfo(self):
        print( f"{ self.title } is of the { self.genre } genre with a total of { self.seasons } seasons." )
        if self.characters:
            print( f"The show features the following characters:")
            for character in  self.characters:
                character.printInfo()



def nativePydantic():

    mulder = Character( first='Fox', last='Mulder', role='Special Agent' )
    mulder.printInfo()
    # prints: Fox Mulder plays the role of Special Agent.

    # == Step 1 ==
    mulder_model_dump = mulder.model_dump()
    # {'first': 'Fox', 'last': 'Mulder', 'role': 'Special Agent'}

    # == Step 2 ==
    mulder_json_dump = json.dumps( mulder_model_dump )
    # '{"first": "Fox", "last": "Mulder", "role": "Special Agent"}'

    # == Step 3 ==
    mulder_model_dump = json.loads( mulder_json_dump )
    # {'first': 'Fox', 'last': 'Mulder', 'role': 'Special Agent'}

    # == Step 4 ==
    mulder = Character( **mulder_model_dump )
    mulder.printInfo()
    # prints: Fox Mulder plays the role of Special Agent.


def pydanticWithATrick1():

    mulder = Character( first='Fox', last='Mulder', role='Special Agent' )
    mulder.printInfo()

    # == Step 1 ==
    mulder_json_dump = ser_des.toJson( mulder, indent=2 )
    '''
    {
        "model": "pyswark.examples.ser_des.Character",
        "contents": {
            "first": "Fox",
            "last": "Mulder",
            "role": "Special Agent"
        }
    }
    '''

    # == Step 2 ==
    mulder = ser_des.fromJson( mulder_json_dump )
    mulder.printInfo()
    # prints: Fox Mulder plays the role of Special Agent.


def pydanticWithATrick2():

    mulder = Character( first='Fox', last='Mulder', role='Special Agent' )
    scully = Character( first='Dana', last='Scully', role='Special Agent & Forensic Pathologist' )

    xFiles = TvShow( title='The X-Files', genre='Science Fiction', seasons=11, characters=[ mulder ] )
    xFiles.characters.append( scully )

    xFiles.printInfo()
    # prints:
    #    The X-Files is of the Science Fiction genre with a total of 11 seasons.
    #    The show features the following characters:
    #    Fox Mulder plays the role of Special Agent.
    #    Dana Scully plays the role of Special Agent & Forensic Pathologist.

    # == Step 1 ==
    xFiles_json_dump = ser_des.toJson( xFiles, indent=2 )
    '''
    {
      "model": "pyswark.examples.ser_des.TvShow",
      "contents": {
        "title": "The X-Files",
        "genre": "Science Fiction",
        "seasons": 11,
        "characters": [
          {
            "first": "Fox",
            "last": "Mulder",
            "role": "Special Agent"
          },
          {
            "first": "Dana",
            "last": "Scully",
            "role": "Special Agent & Forensic Pathologist"
          }
        ]
      }
    }
    '''

    # == Step 2 ==
    xFiles = ser_des.fromJson( xFiles_json_dump )
    xFiles.printInfo()
    # prints:
    #    The X-Files is of the Science Fiction genre with a total of 11 seasons.
    #    The show features the following characters:
    #    Fox Mulder plays the role of Special Agent.
    #    Dana Scully plays the role of Special Agent & Forensic Pathologist.
