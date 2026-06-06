from __future__ import annotations

import asyncio

from app.features.vpn.schemas.usage_history import UsageHistoryPoint, UsageWsUpdate
from app.features.vpn.schemas.usage_live import DeviceUsageLiveResponse
from app.shared.logging_context import structured_extra
from app.shared.usage_ws_manager import usage_ws_manager
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def broadcast_usage_update(
    *,
    aggregate_point: UsageHistoryPoint,
    live: DeviceUsageLiveResponse,
) -> None:
    if usage_ws_manager.connection_count == 0:
        return

    payload = UsageWsUpdate(
        aggregate_point=aggregate_point,
        live=live,
    ).model_dump(mode="json")

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(usage_ws_manager.broadcast(payload))
        else:
            loop.run_until_complete(usage_ws_manager.broadcast(payload))
    except RuntimeError:
        asyncio.run(usage_ws_manager.broadcast(payload))
    except Exception as exc:
        logger.warning(
            "Failed to broadcast usage update",
            extra=structured_extra("usage_broadcast_failed", error=str(exc)),
        )
