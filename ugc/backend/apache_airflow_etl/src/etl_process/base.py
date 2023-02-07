from abc import abstractmethod, ABC


class BaseETL(ABC):
    @abstractmethod
    def run(self):
        pass
