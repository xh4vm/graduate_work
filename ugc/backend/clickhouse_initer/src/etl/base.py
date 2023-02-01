from abc import abstractmethod, ABC


class BaseETL(ABC):
    @abstractmethod
    def run(self):
        """Запуск etl процесса"""
