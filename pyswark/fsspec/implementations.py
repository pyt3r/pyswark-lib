import pydrive2.fs


class GDriveFileSystem( pydrive2.fs.GDriveFileSystem ):
    """GDrive filesystem registered under the ``gdrive2`` protocol."""
    protocol = "gdrive2"
