import json, yaml, io, logging
from typing import Union, List
from abc import ABC, abstractmethod


habloLogger = logging.getLogger("hablo.Config")


class ConfigurationKeyError(KeyError):
    pass
class ConfigurationValueError(ValueError):
    pass



class ConfigurationVariableReference:
    _variableName : str = ""
    _value = None
    def __init__(self, variableName : str = "", value = None):
        self._variableName = variableName
        self._value = value
    
    def getName(self):
        return self._variableName
    
    def setValue(self, value):
        self._value = value

    def getValue(self):
        return self._value

class ConfigurationVariable:
    _variableName : str = ""
    _value = None
    _defaultValue = None
    _typeDef = None
    _references = []
    _isResetting = False
    def __init__(self, variableName : str = "", defaultValue = None, typeDef = None):
        self._isReset = False
        self._references = []
        self._variableName = variableName
        self._value = defaultValue
        self._defaultValue = defaultValue
        if typeDef is None:
            self._typeDef = None
        else:
            self._typeDef = str(typeDef).lower().strip()
    
    def addReference(self, reference : ConfigurationVariableReference):
        self._references.append(reference)
    def removeReference(self, reference : ConfigurationVariableReference):
        self._references.remove(reference)

    def reset(self):
        try:
            self._isResetting = True
            self.setValue(self._defaultValue)
        finally:
            self._isResetting = False

    def setValue(self, value):
        try:
            if self._typeDef is None or self._typeDef == "none" or self._typeDef == "null":
                self._value = value
            elif self._typeDef == "str" or self._typeDef == "string":
                self._value = str(value)
            elif self._typeDef == "list" or self._typeDef == "array":
                self._value = str(value)
            elif self._typeDef == "dict" or self._typeDef == "dictionary" or self._typeDef == "object":
                self._value = str(value)
            elif self._typeDef == "int" or self._typeDef == "integer":
                self._value = str(value)
            elif self._typeDef == "float" or self._typeDef == "double":
                self._value = str(value)
            elif self._typeDef == "bool" or self._typeDef == "boolean":
                self._value = str(value)
            else:
                habloLogger.warning("Invalid type definition '" + str(self._typeDef) + "' for variable: " + str(self._variableName) + ". The value will be set as is.")
                self._value = value
        except:
            self._value = self._defaultValue
        for ref in self._references:
            print("SETTING VALUE: " + self._variableName + " -> " + ref.getName())
            if self._variableName == ref.getName():
                ref.setValue(self._value)
            elif ref.getName().startswith(self._variableName + "."):
                try:
                    v = value
                    for k in ref.getName()[(len(self._variableName) + 1):].split("."):
                        v = v[k]
                    ref.setValue(v)
                except:
                    if not self._isResetting:
                        habloLogger.warning("Failed to set variable reference: " + ref.getName())
                    ref.setValue(None)
            else:
                habloLogger.warning("Found undefined variable reference: " + ref.getName())

    def getName(self):
        return self._variableName
    def getValue(self):
        return self._value

class VariableResolver:
    _variableReferences = {}
    _definedVariables = {}

    def __init__(self):
        pass

    def _resolveParentVariable(self, variableName : str) -> Union[None, str]:
        splitted = variableName.split(".")
        while len(splitted) >= 2:
            k = ".".join(splitted)
            if k in self._definedVariables:
                return self._definedVariables[k].getName()
            splitted.pop()
        return None

    def _resolveVariableFromValue(self, val : str, path : str = "") -> Union[None, ConfigurationVariableReference]:
        if not isinstance(val, str):
            return None
        if val.startswith("${") and val.endswith("}"):
            variableName = val[2:-1].strip()
            parentVariable = self._resolveParentVariable(variableName)
            if parentVariable is None:
                habloLogger.warning("Found undefined variable reference: " + variableName + " at " + path)
            else:
                if not variableName.startswith(parentVariable):
                    if ("nodes." + variableName).startswith(parentVariable):
                        variableName = "nodes." + variableName
            if not (variableName in self._variableReferences):
                self._variableReferences[variableName] = ConfigurationVariableReference(variableName)
                if not (parentVariable is None):
                    self._definedVariables[parentVariable].addReference(self._variableReferences[variableName])
                else:
                    self._variableReferences[variableName].setValue(val) # set the value to the reference
            return self._variableReferences[variableName]
        return None
    def _resolveTreeVariables(self, config, path : str = ""):
        # resolve go through the tree and resolve all variables
        if isinstance(config, dict):
            for key in config:
                val = config[key]
                if isinstance(val, str):
                    cv = self._resolveVariableFromValue(val, (path + "." + str(key)).lstrip("."))
                    if cv is not None:
                        config[key] = cv
                elif isinstance(val, dict) or isinstance(val, list):
                    self._resolveTreeVariables(val, (path + "." + str(key)).lstrip("."))
        elif isinstance(config, list):
            i = 0
            for val in config:
                if isinstance(val, str):
                    cv = self._resolveVariableFromValue(val, (path + "." + str(i)).lstrip("."))
                    if cv is not None:
                        config[i] = cv
                elif isinstance(val, dict) or isinstance(val, list):
                    self._resolveTreeVariables(val, (path + "." + str(i)).lstrip("."))
                i = i + 1
    
    def _resolveDefinedVariables(self, config):
        # we are just intersted in setters (inputs)
        if "inputs" in config:
            for key in config["inputs"]:
                nc = config["inputs"][key].getNativeConfiguration()
                typeDef = None
                varName = "inputs." + key
                varDefault = None
                if "type" in nc:
                    typeDef = nc["type"]
                if "default" in nc:
                    varDefault = nc["default"]
                self._definedVariables[varName] = ConfigurationVariable(varName, varDefault, typeDef)
        # we are just intersted in setters (node.outputs)
        if "nodes" in config:
            for key in config["nodes"]:
                nc = config["nodes"][key].getNativeConfiguration()
                typeDef = None
                varName = "nodes." + key + ".output"
                varDefault = None
                if "outputs" in nc:
                    typeDef = None
                    if "type" in nc["outputs"]:
                        typeDef = nc["outputs"]["type"]
                    if "default" in nc["outputs"]:
                        varDefault = nc["outputs"]["default"]
                self._definedVariables[varName] = ConfigurationVariable(varName, varDefault, typeDef)
                self._definedVariables[key + ".output"] = ConfigurationVariable(varName, varDefault, typeDef)
    
    def resolve(self, config):
        if not isinstance(config, RootConfiguration):
            raise ConfigurationValueError("The configuration object must be an instance of RootConfiguration.")
        self._resolveDefinedVariables(config)
        self._resolveTreeVariables(config.getConfiguration())
    def hasVariable(self, variableName : str) -> bool:
        return variableName in self._definedVariables
    def resetVariables(self):
        for key in self._definedVariables:
            self._definedVariables[key].reset()
    def setVariable(self, variableName : str, value):
        if variableName in self._definedVariables:
            self._definedVariables[variableName].setValue(value)
            return True
        return False
    def getVariable(self, variableName : str) -> Union[ConfigurationVariable, None]:
        if variableName in self._definedVariables:
            return self._definedVariables[variableName]
        return None
    def getVariableReference(self, variableName : str) -> Union[ConfigurationVariableReference, None]:
        if variableName in self._variableReferences:
            return self._variableReferences[variableName]
        return None
    def getReferencedVariables(self) -> List[ConfigurationVariableReference]:
        return list(self._variableReferences.values())


class BaseConfiguration(ABC):
    """
    Base class for all configuration classes that can be used to access configuration data.
    """
    _configuration = {}
    
    def getConfiguration(self):
        return self._configuration
       
    def get(self, path):
        val = self.getValue(path) 
        if isinstance(val, dict) or isinstance(val, list):
            return Configuration(configData = val, parent = self)
        else:
            return val
    def pathExists(self, path):
        _cfg = self._configuration
        try:
            for currentKey in path.split("."):
                _cfg = _cfg[currentKey]
            return True
        except:
            return False

    def getValue(self, path):
        _cfg = self._configuration
        fullCurrentKey = []
        try:
            for currentKey in path.split("."):
                fullCurrentKey.append(currentKey)
                _cfg = _cfg[currentKey]
            return _cfg
        except:
            fullCurrentKey = ".".join(fullCurrentKey)
            if fullCurrentKey == path:
                raise ConfigurationKeyError("The key \"" + fullCurrentKey + "\" does not exist exist.")
            else:
                raise ConfigurationKeyError("The key \"" + fullCurrentKey + "\" does not exist and hence the key \"" + path + "\" does not exist.")

    def getNativeConfiguration(self):
        """
        Returns the configuration data in native python data types.
        It also resolves all variable references.
        """
        return self._dumpNative(False)
    
    def _dumpNative(self, dumpDefinitions : bool = True):
        """
        Dumps the configuration data in native python data types, that can be exported to json or yaml.
        """
        if isinstance(self._configuration, dict):
            d = {}
            for k in self._configuration:
                if isinstance(self._configuration[k], ConfigurationVariableReference):
                    if dumpDefinitions:
                        d[k] = '${' + str(self._configuration[k].getName()) + '}'
                    else:
                        d[k] = self._configuration[k].getValue()
                elif isinstance(self._configuration[k], dict) or isinstance(self._configuration[k], list):
                    d[k] = Configuration(configData = self._configuration[k])._dumpNative()
                else:
                    d[k] = self._configuration[k]
            return d
        elif isinstance(self._configuration, list):
            l = []
            for x in self._configuration:
                if isinstance(x, ConfigurationVariableReference):
                    l.append('${' + str(x.getName()) + '}')
                elif isinstance(x, dict) or isinstance(x, list):
                    l.append(Configuration(configData = x)._dumpNative())
                else:
                    l.append(x)
            return l
        elif isinstance(self._configuration, ConfigurationVariableReference):
            return '${' + str(self._configuration.getName()) + "}"
        else:
            return self._configuration
    
    def dump(self, format : str ="yaml", raw : bool = False) -> str:
        if format == "json":
            return str(json.dumps(self._dumpNative())).rstrip()
        elif format == "yaml":
            if raw:
                return str(yaml.dump(self._configuration)).rstrip()
            else:
                return str(yaml.dump(self._dumpNative())).rstrip()
        else:
            raise ConfigurationValueError("Invalid format specified. Please use either json or yaml.")

    def __getitem__(self, key):
        if isinstance(self._configuration[key], dict) or isinstance(self._configuration[key], list):
            return Configuration(configData = self._configuration[key])
        else:
            return self._configuration[key] 

    def __iter__(self):
        if isinstance(self._configuration, dict):
            for x in self._configuration:
                yield x
        elif isinstance(self._configuration, list):
            i = 0
            for x in self._configuration:
                yield i
                i = i + 1
        else:
            raise ConfigurationValueError("You cannot iterate a type that is not iteratable.")



class Configuration(BaseConfiguration):
    """
    Represents a configuration object that can be used to access configuration data.
    This is the base class for all nodes within the configuration tree.
    """
    _parent = None

    def __init__(self, configData = None, parent : Union[BaseConfiguration, None] = None):
        if configData is not None:
            self._configuration = configData
        else:
            self._configuration = {}
        self._parent = parent

    def getParent(self) -> Union[BaseConfiguration, None]:
        return self._parent




class RootConfiguration(BaseConfiguration):
    """
    Base class for all configuration classes that configuration can be reloaded from.
    It represents the root of the configuration tree.
    """
    _variableResolver = None

    def getVariableResolver(self) -> Union[None, VariableResolver]:
        """
        Returns the variable resolver object associated with this configuration.
        It can be used to set and get variables and propagate changes to the configuration tree.
        """
        return self._variableResolver

    @abstractmethod
    def reload(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def _dataReloaded(self):
        """
        This method is called after the configuration data is reloaded.
        """
        self._variableResolver = VariableResolver()
        self._variableResolver.resolve(self)
        self._variableResolver.resetVariables()


class FileConfiguration(RootConfiguration):
    """
    Represents a configuration object that can be used to access configuration data stored in files.
    It supports both json and yaml file formats.
    """
    configpath : str = ""

    def __init__(self, configpath: str):
        self.configpath = configpath
        self.reload()

    def reload(self):
        suffix = self.configpath.split(".")[-1].lower()
        with open(self.configpath, "r") as f:
            # if configpath ends with .json
            if suffix == "json":
                self._configuration = json.load(f)
            elif suffix in ["yaml", "yml"]:
                self._configuration = yaml.safe_load(f)
        self._dataReloaded()

class JsonStreamConfiguration(RootConfiguration):
    """
    Represents a configuration object that can be used to access configuration json data from a stream.
    """
    _stream = None

    def __init__(self, stream : io.TextIOBase):
        self._stream = stream
        self.reload()

    def reload(self):
        self._stream.seek(0)
        self._configuration = json.load(self._stream)
        self._dataReloaded()

class YamlStreamConfiguration(RootConfiguration):
    """
    Represents a configuration object that can be used to access configuration yaml data from a stream.
    """
    _stream = None

    def __init__(self, stream: io.TextIOBase):
        self._stream = stream
        self.reload()

    def reload(self):
        # reset the stream to the beginning
        self._stream.seek(0)
        self._configuration = yaml.safe_load(self._stream)
        self._dataReloaded()




