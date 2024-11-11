from .Channels import Channel, GunicornChannel
from .Config import RootConfiguration, FileConfiguration
from typing import Union



def mucho(
    con : Channel = GunicornChannel(),
    configuration : Union[RootConfiguration, None] = None
):
    if configuration is not None:
        configuration = FileConfiguration(configpath="hablo.yaml")
    con.setConfiguration(configuration)

