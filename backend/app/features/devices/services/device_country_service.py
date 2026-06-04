from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.features.client_behavior.repositories.behavior_rollup_country import parse_country_counts
from app.features.client_behavior.repositories.behavior_rollup_repository import BehaviorRollupRepository
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.devices.schemas.device_country import (
    CountryCountItem,
    DeviceCountryBreakdownRead,
    DeviceCountrySummaryItem,
    DeviceCountrySummaryList,
)
from app.shared.domain_country import country_display_name
from fastapi import HTTPException


class DeviceCountryService:
    def __init__(self, db: Session):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.rollup_repo = BehaviorRollupRepository(db)

    def get_breakdown(self, device_id: int, *, period_hours: int = 168) -> DeviceCountryBreakdownRead:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        hours = max(1, min(period_hours, 24 * 30))
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        rollups = self.rollup_repo.get_rollups_for_device(device_id, since)

        totals = self._sum_country_counts(rollups)
        countries, primary = self._build_country_items(totals)
        total_queries = sum(totals.values())

        note = None
        if total_queries == 0:
            note = "No DNS activity recorded for this device in the selected period yet."

        return DeviceCountryBreakdownRead(
            device_id=device_id,
            period_hours=hours,
            total_queries=total_queries,
            primary_country_code=primary[0] if primary else None,
            primary_country_name=primary[1] if primary else None,
            countries=countries,
            note=note,
        )

    def list_summaries(self, *, period_hours: int = 168) -> DeviceCountrySummaryList:
        hours = max(1, min(period_hours, 24 * 30))
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        devices = self.device_repo.get_all()
        items: List[DeviceCountrySummaryItem] = []

        for device in devices:
            rollups = self.rollup_repo.get_rollups_for_device(device.id, since)
            totals = self._sum_country_counts(rollups)
            _, primary = self._build_country_items(totals)
            items.append(
                DeviceCountrySummaryItem(
                    device_id=device.id,
                    primary_country_code=primary[0] if primary else None,
                    primary_country_name=primary[1] if primary else None,
                )
            )

        return DeviceCountrySummaryList(items=items, period_hours=hours)

    @staticmethod
    def _sum_country_counts(rollups) -> Dict[str, int]:
        totals: Dict[str, int] = {}
        for rollup in rollups:
            for code, count in parse_country_counts(rollup.country_counts_json).items():
                totals[code] = totals.get(code, 0) + count
        return totals

    @staticmethod
    def _build_country_items(
        totals: Dict[str, int],
    ) -> Tuple[List[CountryCountItem], Optional[Tuple[str, str]]]:
        total = sum(totals.values())
        if total <= 0:
            return [], None

        sorted_items = sorted(totals.items(), key=lambda x: (-x[1], x[0]))
        countries: List[CountryCountItem] = []
        for code, count in sorted_items[:12]:
            countries.append(
                CountryCountItem(
                    country_code=code,
                    country_name=country_display_name(code),
                    query_count=count,
                    share_percent=round(100.0 * count / total, 1),
                )
            )

        primary_code = sorted_items[0][0]
        for code, _count in sorted_items:
            if code != "GLOBAL":
                primary_code = code
                break

        return countries, (primary_code, country_display_name(primary_code))
