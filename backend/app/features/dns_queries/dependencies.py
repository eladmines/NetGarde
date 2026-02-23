from app.features.dns_queries.services.dns_query_service import DnsQueryService
from app.features.dns_queries.services.dns_query_service_interface import IDnsQueryService


def get_dns_query_service() -> IDnsQueryService:
    """Dependency to get DnsQueryService instance."""
    return DnsQueryService()
