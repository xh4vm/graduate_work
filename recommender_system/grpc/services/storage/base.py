from abc import ABC, abstractmethod, abstractproperty


class BaseDB(ABC):
    @abstractproperty
    def conn(self):
        '''Клиент БД'''

    @abstractmethod
    def get(self):
        '''Метод получения данных'''
