"""
This is the template_class.py
"""


class TemplateClass:
    """A class that performs the a template method."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def template_method(self):
        """
        a template method to a template class

        Parameters
        ----------

        Returns
        -------
        result : number
            the sum of x and y
        """

        try:
            return self.x + self.y
        except BaseException:
            print('Something went wrong. Make sure x and y are both numbers')
