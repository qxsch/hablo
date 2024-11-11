from ..Config import RootConfiguration


class Orchestrator:
    _configuration : RootConfiguration = None

    def __init__(self, configuration : RootConfiguration):
        self._configuration = configuration

    def setConfiguration(self, configuration : RootConfiguration):
        self._configuration = configuration


_globalNodeTypeHandlers = {}
def setGlobalNodeHandler(typeName : str, handler):
    typeName = str(typeName).lower().strip()
    if typeName in _globalNodeTypeHandlers:
        raise ValueError("Node type handler already exists for type: " + typeName)
    _globalNodeTypeHandlers[typeName] = handler


class FlowPlanner:
    _inputs = []
    _nodes = []
    _outputs = []

    def __init__(self, configuration : RootConfiguration):
        self._setInputs(configuration)
        self._setOutputs(configuration)
        self._setNodes(configuration)
        pass

    def _setInputs(self, configuration : RootConfiguration):
        self._inputs = []
        if "inputs" not in configuration.getConfiguration():
            raise ValueError("No inputs found in configuration")
        
        if len(self._inputs) == 0:
            raise ValueError("No inputs found in configuration")
    

    def _setOutputs(self, configuration : RootConfiguration):
        self._outputs = []
        if "outputs" not in configuration.getConfiguration():
            raise ValueError("No outputs found in configuration")
        
        if len(self._outputs) == 0:
            raise ValueError("No outputs found in configuration")
    

    def _setNodes(self, configuration : RootConfiguration):
        self._nodes = []
        if "nodes" not in configuration.getConfiguration():
            raise ValueError("No nodes found in configuration")
        
        if len(self._nodes) == 0:
            raise ValueError("No nodes found in configuration")
