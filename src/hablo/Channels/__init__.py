from abc import ABC, abstractmethod
from ..Config import RootConfiguration

class Channel(ABC):
    _configuration : RootConfiguration = None
    _flow_orchestrator = None

    def setConfiguration(self, configuration : RootConfiguration):
        self._configuration = configuration

    def setFlowOrchestrator(self, flow_orchestrator):
        self._flow_orchestrator = flow_orchestrator

    @abstractmethod
    def run(self):
        raise NotImplementedError("Subclasses must implement this method")


class ConsoleChannel(Channel):
    def run(self):
        print("Console is running")

class GunicornChannel(Channel):
    def run(self):
        print("Gunicorn is running")


__all__ = ['Channel', 'GunicornChannel', 'ConsoleChannel']

