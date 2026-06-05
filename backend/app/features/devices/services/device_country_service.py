from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.features.client_behavior.repositories.behavior_rollup_country import parse_country_counts
from app.features.client_behavior.repositories.behavior_rollup_repository import BehaviorRollupRepository
from app.features.devices.repositories.device_country_presence_repository import (
    DeviceCountryPresenceRepository,
)
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.devices.schemas.device_country import (
    CountryCountItem,
    DeviceCountryBreakdownRead,
    DeviceCountrySummaryItem,
    DeviceCountrySummaryList,
)
from app.shared.domain_country import country_display_name
from fastapi import HTTPException


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class DeviceCountryService:
    def __init__(self, db: Session):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.rollup_repo = BehaviorRollupRepository(db)
        self.presence_repo = DeviceCountryPresenceRepository(db)

    def get_breakdown(self, device_id: int, *, period_hours: int = 168) -> DeviceCountryBreakdownRead:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        hours = max(1, min(period_hours, 24 * 30))
        since = datetime.now(timezone.utc) - timedelta(hours=hours)

        presences = self.presence_repo.list_for_device(device_id)
        active = [p for p in presences if _as_utc(p.last_seen_at) >= since]

        if active:
            totals = {p.country_code: p.query_count for p in active}
            countries, primary = self._build_country_items(active, totals)
            total_queries = sum(totals.values())
            known_count = len(presences)
            note = None
            if total_queries == 0:
                note = "No DNS activity in the selected period."
        else:
            rollups = self.rollup_repo.get_rollups_for_device(device_id, since)
            totals = self._sum_country_counts(rollups)
            countries, primary = self._build_country_items_from_totals(totals)
            total_queries = sum(totals.values())
            known_count = len(presences)
            note = (
                "Country regions are inferred from domain endings (.il, .de, .co.uk, etc.). "
                "Alerts fire when a device uses a region for the first time."
            )
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
            known_regions_count=known_count,
        )

    def list_summaries(self, *, period_hours: int = 168) -> DeviceCountrySummaryList:
        hours = max(1, min(period_hours, 24 * 30))
        devices = self.device_repo.get_all()
        items: List[DeviceCountrySummaryItem] = []

        for device in devices:
            presences = self.presence_repo.list_for_device(device.id)
            if presences:
                totals = {p.country_code: p.query_count for p in presences}
                _, primary = self._build_country_items_from_totals(totals)
            else:
                since = datetime.now(timezone.utc) - timedelta(hours=hours)
                rollups = self.rollup_repo.get_rollups_for_device(device.id, since)
                totals = self._sum_country_counts(rollups)
                _, primary = self._build_country_items_from_totals(totals)
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

    def _build_country_items(
        self,
        presences,
        totals: Dict[str, int],
    ) -> Tuple[List[CountryCountItem], Optional[Tuple[str, str]]]:
        total = sum(totals.values())
        if total <= 0:
            return [], None

        by_code = {p.country_code: p for p in presences}
        sorted_items = sorted(totals.items(), key=lambda x: (-x[1], x[0]))
        countries: List[CountryCountItem] = []
        window_start = datetime.now(timezone.utc) - timedelta(hours=48)

        for code, count in sorted_items[:12]:
            row = by_code.get(code)
            first_seen = _as_utc(row.first_seen_at) if row and row.first_seen_at else None
            last_seen = _as_utc(row.last_seen_at) if row and row.last_seen_at else None
            countries.append(
                CountryCountItem(
                    country_code=code,
                    country_name=country_display_name(code),
                    query_count=count,
                    share_percent=round(100.0 * count / total, 1),
                    first_seen_at=first_seen,
                    last_seen_at=last_seen,
                    is_new=bool(first_seen and first_seen >= window_start),
                )
            )

        _, primary = self._build_country_items_from_totals(totals)
        return countries, primary

    @staticmethod
    def _build_country_items_from_totals(
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
