import abc


class FileHandlerInterface(metaclass=abc.ABCMeta):
    """Interface to handle multiple Files"""

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'load_all_files') and callable(subclass.load_all_files) and
                hasattr(subclass, 'get_fastas') and callable(subclass.get_fastas) and
                hasattr(subclass, 'get_gtfs') and callable(subclass.get_gtfs) or
                NotImplemented)

    @abc.abstractmethod
    def load_all_files(self, path):
        """Load in all files of a folder"""
        raise NotImplementedError

