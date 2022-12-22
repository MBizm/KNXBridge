class ApplianceBase:
    """
    basic appliance implementation
    """
    def getName(self) -> str:
        """
        abstract implementation to define appliance type name in derived classes
        """
        pass

    def getAttribute(self, name, format, attr, section=None):
        raise NotImplementedError

    def setAttribute(self, attr, val, function):
        raise NotImplementedError