from atlas.common.http import AtlasHttpClient
from atlas.discovery.connectors.greenhouse import GreenhouseConnector
from atlas.discovery.mappers.greenhouse import GreenhouseJobMapper
from atlas.discovery.service import DiscoveryService


class Atlas:
    def __init__(self) -> None:
        client = AtlasHttpClient()

        greenhouse = GreenhouseConnector(
            client=client,
            mapper=GreenhouseJobMapper(),
        )

        self.discovery = DiscoveryService(
            connectors=[greenhouse],
        )
