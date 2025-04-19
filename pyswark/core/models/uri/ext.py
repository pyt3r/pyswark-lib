
class Ext:

    def __init__(self, name):
        self._name = name

    @property
    def full(self):
        """ i.e. file.csv.gz -> csv.gz """
        if not self._name:
            return ''

        name, *parts = self._name.split('.')
        return '.'.join( list( parts ))

    @property
    def root(self):
        """ i.e. file.csv.gz -> csv """
        if not self.full:
            return ''

        *parts, absolute = self.full.split('.')
        return '.'.join( list( parts )[:1] )

    @property
    def absolute(self):
        """ i.e. file.csv.gz -> gz """
        if not self.full:
            return ''

        *parts, absolute = self.full.split('.')
        return absolute
