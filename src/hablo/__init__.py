from .Channels import Channel, GunicornChannel
from .Config import RootConfiguration, FileConfiguration
from typing import Union



def mucho(
    con : Channel = GunicornChannel(),
    configuration : Union[RootConfiguration, None] = None
):
    """
    Main Unified Chat-Host Orchestration (MUCHO) function
    This is the main entry point for the hablo library
    usage: hablo.mucho(con=Channel)
    """
    if configuration is not None:
        configuration = FileConfiguration(configpath="hablo.yaml")
    con.setConfiguration(configuration)

