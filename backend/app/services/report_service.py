"""
Report Service - Urbain Sustainability System
Service métier pour la gestion des rapports et analyses
"""

import uuid
import structlog
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, and_, or_

from app.services.base import BaseService
from app.models.report import Report, ReportType, ReportStatus, ReportFrequency
from app.models.signal import Signal, SignalStatus
from app.schemas.report import ReportCreate, ReportUpdate
from app.repositories import ReportRepository
from app.core.exceptions import (
    DatabaseError, NotFoundError, ValidationError,
    BusinessLogicError, ExternalServiceError
)

logger = structlog.get_logger()


class ReportService(BaseService[Report, ReportCreate, ReportUpdate]):
    """
    Service métier pour la génération et gestion des rapports
    Intègre les données IA, les analytics et les exports
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repository = ReportRepository(db, Report)

    async def _generate_report_code(self, report_type: ReportType) -> str:
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%m")
        type_prefix = report_type.value[:3].upper()
        unique = str(uuid.uuid4())[:4].upper()
        return f"RPT-{type_prefix}-{year}{month}-{unique}"

    async def create_report(self, obj_in: ReportCreate) -> Report:
        try:
            obj_data = obj_in.model_dump()
            try:
                rt = ReportType(obj_data["report_type"])
            except ValueError:
                raise ValidationError(f"Invalid report type: {obj_data['report_type']}")

            rf = ReportFrequency(obj_data.get("frequency", "on_demand"))

            report_code = await self._generate_report_code(rt)

            report = Report(
                title=obj_data["title"],
                description=obj_data.get("description"),
                report_code=report_code,
                signal_id=obj_data.get("signal_id"),
                generated_by=obj_data.get("generated_by"),
                sector_id=obj_data.get("sector_id"),
                report_type=rt,
                status=ReportStatus.GENERATING,
                frequency=rf,
                start_date=obj_data.get("start_date"),
                end_date=obj_data.get("end_date"),
                analysis_period_hours=obj_data.get("analysis_period_hours"),
                ai_model_version=obj_data.get("ai_model_version"),
                ai_parameters=obj_data.get("ai_parameters"),
                is_public=obj_data.get("is_public", False),
                auto_share_enabled=obj_data.get("auto_share_enabled", False),
                notification_enabled=obj_data.get("notification_enabled", True),
                tags=obj_data.get("tags")
            )

            self.db.add(report)
            await self.db.commit()
            await self.db.refresh(report)

            await self.log_operation("create_report", {"report_id": report.id, "code": report_code})
            return report
        except ValidationError:
            raise
        except Exception as e:
            await self.log_error("create_report", e)
            raise DatabaseError(f"Failed to create report: {str(e)}")

    async def get_report(self, report_id: int) -> Report:
        try:
            report = await self.repository.get_report_with_relations(report_id=report_id)
            if not report:
                raise NotFoundError(f"Report with id {report_id} not found")
            return report
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("get_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to get report: {str(e)}")

    async def update_report(self, report_id: int, obj_in: ReportUpdate) -> Report:
        try:
            report = await self.get_report(report_id)

            if report.status == ReportStatus.COMPLETED:
                raise BusinessLogicError("Cannot update a completed report")
            if report.status == ReportStatus.ARCHIVED:
                raise BusinessLogicError("Cannot update an archived report")

            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(report, field):
                    setattr(report, field, value)

            await self.db.commit()
            await self.db.refresh(report)

            await self.log_operation("update_report", {"report_id": report_id})
            return report
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("update_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to update report: {str(e)}")

    async def delete_report(self, report_id: int) -> bool:
        try:
            report = await self.get_report(report_id)
            await self.repository.remove(id=report_id)
            await self.log_operation("delete_report", {"report_id": report_id})
            return True
        except NotFoundError:
            raise
        except Exception as e:
            await self.log_error("delete_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to delete report: {str(e)}")

    async def get_reports(self, skip: int = 0, limit: int = 100,
                           filters: Optional[Dict[str, Any]] = None) -> List[Report]:
        try:
            if filters:
                return await self.repository.get_reports_with_filters(
                    filters=filters, skip=skip, limit=limit
                )
            return await self.repository.get_multi(skip=skip, limit=limit)
        except Exception as e:
            await self.log_error("get_reports", e)
            raise DatabaseError(f"Failed to get reports: {str(e)}")

    async def generate_report(self, report_id: int) -> Report:
        try:
            report = await self.get_report(report_id)
            report.status = ReportStatus.GENERATING
            await self.db.commit()

            try:
                if report.report_type == ReportType.SIGNAL_ANALYSIS and report.signal_id:
                    await self._populate_signal_analysis(report)
                elif report.report_type == ReportType.PRIORITY_ASSESSMENT:
                    await self._populate_priority_assessment(report)
                elif report.report_type == ReportType.TREND_ANALYSIS:
                    await self._populate_trend_analysis(report)
                elif report.report_type == ReportType.PERFORMANCE_METRICS:
                    await self._populate_performance_metrics(report)
                elif report.report_type == ReportType.SECTOR_SUMMARY and report.sector_id:
                    await self._populate_sector_summary(report)
                elif report.report_type == ReportType.CITIZEN_FEEDBACK:
                    await self._populate_citizen_feedback(report)
                else:
                    await self._populate_generic_analysis(report)

                report.mark_as_completed()
                await self.db.commit()
                await self.db.refresh(report)

            except Exception as gen_error:
                report.mark_as_failed(str(gen_error))
                await self.db.commit()
                await self.db.refresh(report)
                raise ExternalServiceError(f"Report generation failed: {str(gen_error)}")

            await self.log_operation("generate_report", {"report_id": report_id})
            return report
        except (NotFoundError, ExternalServiceError):
            raise
        except Exception as e:
            await self.log_error("generate_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to generate report: {str(e)}")

    async def _populate_signal_analysis(self, report: Report) -> None:
        signal_query = select(Signal).where(Signal.id == report.signal_id)
        signal_result = await self.db.execute(signal_query)
        signal = signal_result.scalar_one_or_none()
        if not signal:
            raise NotFoundError(f"Signal {report.signal_id} not found for analysis")

        report.summary = f"Analysis of signal {signal.reference_number}: {signal.title}"
        report.key_findings = [
            {"category": "Status", "value": signal.status.value},
            {"category": "Priority", "value": str(signal.priority_id)},
            {"category": "AI Confidence", "value": signal.ai_confidence_score}
        ]
        report.total_signals_analyzed = 1

    async def _populate_priority_assessment(self, report: Report) -> None:
        if report.start_date and report.end_date:
            signals_query = select(Signal).where(
                and_(
                    Signal.created_at >= report.start_date,
                    Signal.created_at <= report.end_date
                )
            )
        else:
            signals_query = select(Signal)

        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()

        total = len(signals)
        critical = sum(1 for s in signals if s.ai_priority_score and s.ai_priority_score >= 0.8)
        high = sum(1 for s in signals if s.ai_priority_score and 0.6 <= s.ai_priority_score < 0.8)

        report.summary = f"Priority assessment of {total} signals"
        report.total_signals_analyzed = total
        report.critical_signals_count = critical
        report.high_priority_count = high

        report.priority_breakdown = {
            "critical": critical,
            "high": high,
            "medium": total - critical - high
        }

    async def _populate_trend_analysis(self, report: Report) -> None:
        end = report.end_date or datetime.now(timezone.utc)
        start = report.start_date or (end - timedelta(days=30))

        signals_query = select(Signal).where(
            and_(Signal.created_at >= start, Signal.created_at <= end)
        )
        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()

        total = len(signals)
        resolved = sum(1 for s in signals if s.status == SignalStatus.RESOLVED)
        satisfaction = sum(s.citizen_satisfaction or 0 for s in signals if s.citizen_satisfaction)
        satisfaction_count = sum(1 for s in signals if s.citizen_satisfaction)

        report.summary = f"Trend analysis from {start.date()} to {end.date()}"
        report.total_signals_analyzed = total
        report.avg_resolution_time_hours = await self._calculate_avg_resolution(signals)
        report.citizen_satisfaction_rate = (satisfaction / satisfaction_count * 20) if satisfaction_count > 0 else 0

    async def _populate_performance_metrics(self, report: Report) -> None:
        end = report.end_date or datetime.now(timezone.utc)
        start = report.start_date or (end - timedelta(days=30))

        signals_query = select(Signal).where(
            and_(Signal.created_at >= start, Signal.created_at <= end)
        )
        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()

        total = len(signals)
        resolved = sum(1 for s in signals if s.status == SignalStatus.RESOLVED)
        avg_resolution = await self._calculate_avg_resolution(signals)

        report.summary = f"Performance metrics for period {start.date()} to {end.date()}"
        report.total_signals_analyzed = total
        report.avg_resolution_time_hours = avg_resolution

        report.system_performance = {
            "total_signals": total,
            "resolved_signals": resolved,
            "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0,
            "avg_resolution_hours": avg_resolution,
            "period_days": (end - start).days
        }

    async def _populate_sector_summary(self, report: Report) -> None:
        signals_query = select(Signal).where(
            Signal.assigned_sector_id == report.sector_id
        )
        if report.start_date:
            signals_query = signals_query.where(Signal.created_at >= report.start_date)
        if report.end_date:
            signals_query = signals_query.where(Signal.created_at <= report.end_date)

        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()

        total = len(signals)
        resolved = sum(1 for s in signals if s.status == SignalStatus.RESOLVED)

        report.summary = f"Sector {report.sector_id} summary with {total} signals"
        report.total_signals_analyzed = total

        report.sector_performance = {
            "total_signals": total,
            "resolved_signals": resolved,
            "resolution_rate": round((resolved / total * 100), 2) if total > 0 else 0
        }

    async def _populate_citizen_feedback(self, report: Report) -> None:
        signals_query = select(Signal)
        if report.start_date:
            signals_query = signals_query.where(Signal.created_at >= report.start_date)
        if report.end_date:
            signals_query = signals_query.where(Signal.created_at <= report.end_date)

        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()

        satisfaction_values = [s.citizen_satisfaction for s in signals if s.citizen_satisfaction]
        avg_satisfaction = sum(satisfaction_values) / len(satisfaction_values) if satisfaction_values else 0

        report.summary = f"Citizen feedback analysis based on {len(signals)} signals"
        report.total_signals_analyzed = len(signals)
        report.citizen_satisfaction_rate = round(avg_satisfaction * 20, 2) if avg_satisfaction else 0

        recommendations = []
        if avg_satisfaction and avg_satisfaction < 3:
            recommendations.append("Improve response times to increase citizen satisfaction")
        if avg_satisfaction and avg_satisfaction >= 4:
            recommendations.append("Maintain current service quality levels")

        report.recommendations = recommendations if recommendations else [
            {"type": "general", "message": "Continue monitoring citizen satisfaction trends"}
        ]

    async def _populate_generic_analysis(self, report: Report) -> None:
        end = report.end_date or datetime.now(timezone.utc)
        start = report.start_date or (end - timedelta(days=30))

        signals_query = select(Signal).where(
            and_(Signal.created_at >= start, Signal.created_at <= end)
        )
        signals_result = await self.db.execute(signals_query)
        signals = signals_result.scalars().all()

        total = len(signals)
        report.summary = f"Generic analysis of {total} signals"
        report.total_signals_analyzed = total

    async def _calculate_avg_resolution(self, signals: List[Signal]) -> float:
        resolved_times = []
        for s in signals:
            if s.resolved_at and s.created_at:
                delta = (s.resolved_at - s.created_at).total_seconds() / 3600
                resolved_times.append(delta)
        return round(sum(resolved_times) / len(resolved_times), 2) if resolved_times else 0

    async def generate_signal_report(self, signal_id: int, generated_by: int) -> Report:
        try:
            report_in = ReportCreate(
                title=f"Signal Analysis Report #{signal_id}",
                report_type=ReportType.SIGNAL_ANALYSIS.value,
                signal_id=signal_id,
                generated_by=generated_by,
                frequency=ReportFrequency.ON_DEMAND.value
            )
            report = await self.create_report(report_in)
            return await self.generate_report(report.id)
        except Exception as e:
            await self.log_error("generate_signal_report", e, {"signal_id": signal_id})
            raise DatabaseError(f"Failed to generate signal report: {str(e)}")

    async def generate_sector_report(self, sector_id: int, generated_by: int,
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None) -> Report:
        try:
            report_in = ReportCreate(
                title=f"Sector Performance Report #{sector_id}",
                report_type=ReportType.SECTOR_SUMMARY.value,
                sector_id=sector_id,
                generated_by=generated_by,
                start_date=start_date,
                end_date=end_date,
                frequency=ReportFrequency.ON_DEMAND.value
            )
            report = await self.create_report(report_in)
            return await self.generate_report(report.id)
        except Exception as e:
            await self.log_error("generate_sector_report", e, {"sector_id": sector_id})
            raise DatabaseError(f"Failed to generate sector report: {str(e)}")

    async def generate_trend_report(self, generated_by: int,
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Report:
        try:
            report_in = ReportCreate(
                title=f"Trend Analysis Report",
                report_type=ReportType.TREND_ANALYSIS.value,
                generated_by=generated_by,
                start_date=start_date,
                end_date=end_date,
                frequency=ReportFrequency.ON_DEMAND.value
            )
            report = await self.create_report(report_in)
            return await self.generate_report(report.id)
        except Exception as e:
            await self.log_error("generate_trend_report", e)
            raise DatabaseError(f"Failed to generate trend report: {str(e)}")

    async def generate_performance_report(self, generated_by: int,
                                           start_date: Optional[datetime] = None,
                                           end_date: Optional[datetime] = None) -> Report:
        try:
            report_in = ReportCreate(
                title=f"Performance Metrics Report",
                report_type=ReportType.PERFORMANCE_METRICS.value,
                generated_by=generated_by,
                start_date=start_date,
                end_date=end_date,
                frequency=ReportFrequency.ON_DEMAND.value
            )
            report = await self.create_report(report_in)
            return await self.generate_report(report.id)
        except Exception as e:
            await self.log_error("generate_performance_report", e)
            raise DatabaseError(f"Failed to generate performance report: {str(e)}")

    async def generate_citizen_feedback_report(self, generated_by: int,
                                                start_date: Optional[datetime] = None,
                                                end_date: Optional[datetime] = None) -> Report:
        try:
            report_in = ReportCreate(
                title=f"Citizen Feedback Report",
                report_type=ReportType.CITIZEN_FEEDBACK.value,
                generated_by=generated_by,
                start_date=start_date,
                end_date=end_date,
                frequency=ReportFrequency.ON_DEMAND.value
            )
            report = await self.create_report(report_in)
            return await self.generate_report(report.id)
        except Exception as e:
            await self.log_error("generate_citizen_feedback_report", e)
            raise DatabaseError(f"Failed to generate citizen feedback report: {str(e)}")

    async def generate_priority_assessment(self, generated_by: int,
                                            sector_id: Optional[int] = None,
                                            priority_level: Optional[int] = None,
                                            start_date: Optional[datetime] = None,
                                            end_date: Optional[datetime] = None) -> Report:
        try:
            title = f"Priority Assessment Report"
            if sector_id:
                title += f" (Sector #{sector_id})"
            if priority_level:
                title += f" (Level {priority_level})"
            report_in = ReportCreate(
                title=title,
                report_type=ReportType.PRIORITY_ASSESSMENT.value,
                generated_by=generated_by,
                sector_id=sector_id,
                start_date=start_date,
                end_date=end_date,
                frequency=ReportFrequency.ON_DEMAND.value
            )
            report = await self.create_report(report_in)
            return await self.generate_report(report.id)
        except Exception as e:
            await self.log_error("generate_priority_assessment", e)
            raise DatabaseError(f"Failed to generate priority assessment: {str(e)}")

    async def get_report_stats(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            return await self.repository.get_report_statistics(filters=filters)
        except Exception as e:
            await self.log_error("get_report_stats", e)
            raise DatabaseError(f"Failed to get report stats: {str(e)}")

    async def schedule_report(self, report_id: int, frequency: str,
                               schedule_config: Dict[str, Any]) -> Report:
        try:
            report = await self.get_report(report_id)

            try:
                rf = ReportFrequency(str(frequency).lower())
            except ValueError:
                raise ValidationError(f"Invalid frequency: {frequency}")

            report.frequency = rf
            if not report.meta_data:
                report.meta_data = {}
            report.meta_data["schedule_config"] = schedule_config
            report.meta_data["scheduled_at"] = datetime.now(timezone.utc).isoformat()
            report.status = ReportStatus.SCHEDULED

            await self.db.commit()
            await self.db.refresh(report)

            await self.log_operation("schedule_report", {"report_id": report_id, "frequency": frequency})
            return report
        except (NotFoundError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("schedule_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to schedule report: {str(e)}")

    async def archive_report(self, report_id: int) -> Report:
        try:
            report = await self.get_report(report_id)

            if report.status == ReportStatus.ARCHIVED:
                raise BusinessLogicError("Report is already archived")

            report.status = ReportStatus.ARCHIVED
            await self.db.commit()
            await self.db.refresh(report)

            await self.log_operation("archive_report", {"report_id": report_id})
            return report
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            await self.log_error("archive_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to archive report: {str(e)}")

    async def export_report(self, report_id: int, export_format: str = "pdf") -> Dict[str, Any]:
        try:
            report = await self.get_report(report_id)

            if report.status != ReportStatus.COMPLETED:
                raise BusinessLogicError("Cannot export a non-completed report")

            valid_formats = ["pdf", "xlsx", "csv", "json"]
            if export_format not in valid_formats:
                raise ValidationError(f"Invalid export format. Must be one of: {valid_formats}")

            export_data = {
                "report_id": report.id,
                "report_code": report.report_code,
                "title": report.title,
                "type": report.report_type.value,
                "format": export_format,
                "summary": report.summary,
                "key_findings": report.key_findings,
                "recommendations": report.recommendations,
                "metrics": {
                    "total_signals": report.total_signals_analyzed,
                    "critical_count": report.critical_signals_count,
                    "high_priority_count": report.high_priority_count,
                    "avg_resolution_time": report.avg_resolution_time_hours,
                    "satisfaction_rate": report.citizen_satisfaction_rate
                },
                "generated_at": report.generated_at.isoformat() if report.generated_at else None,
                "export_timestamp": datetime.now(timezone.utc).isoformat()
            }

            if not report.file_urls:
                report.file_urls = []
            export_url = f"/exports/reports/{report.report_code}.{export_format}"
            report.file_urls.append(export_url)
            await self.db.commit()

            await self.log_operation("export_report", {
                "report_id": report_id, "format": export_format
            })
            return export_data
        except (NotFoundError, BusinessLogicError, ValidationError):
            raise
        except Exception as e:
            await self.log_error("export_report", e, {"report_id": report_id})
            raise DatabaseError(f"Failed to export report: {str(e)}")
