from atlas.common.http import AtlasHttpClient
from atlas.discovery.connectors.ashby import AshbyConnector
from atlas.discovery.connectors.greenhouse import GreenhouseConnector
from atlas.discovery.connectors.lever import LeverConnector
from atlas.discovery.mappers.ashby import AshbyJobMapper
from atlas.discovery.mappers.greenhouse import GreenhouseJobMapper
from atlas.discovery.mappers.lever import LeverJobMapper
from atlas.discovery.service import DiscoveryService
from atlas.matching.service import MatchingService
from atlas.ranking.service import RankingService


class Atlas:
    def __init__(self) -> None:
        client = AtlasHttpClient()

        greenhouse = GreenhouseConnector(
            client=client,
            mapper=GreenhouseJobMapper(),
        )

        lever = LeverConnector(
            client=client,
            mapper=LeverJobMapper(),
        )

        ashby = AshbyConnector(
            client=client,
            mapper=AshbyJobMapper(),
        )

        self.discovery = DiscoveryService(
            connectors=[greenhouse, lever, ashby],
        )

        self.matching = MatchingService()

        self.ranking = RankingService()
