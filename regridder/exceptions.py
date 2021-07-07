class BadAreaDefinition(Exception):
    """Exception raised for errors in the definition of area
    """

    def __str__(self):
        return "Area can not be defined"
