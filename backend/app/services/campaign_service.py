from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pandas as pd
import json
from app.models.planning import CampaignPacing, MediaPlan, PacingStatus

class CampaignService:
    def __init__(self, db: Session):
        self.db = db

    def update_campaign_pacing(self, plan_id: int, pacing_data: Dict[str, Any]) -> CampaignPacing:
        # Calculate pacing status
        planned_spend = pacing_data.get('planned_spend', 0)
        actual_spend = pacing_data.get('actual_spend', 0)
        
        # Calculate pacing percentage
        if planned_spend > 0:
            pacing_percentage = (actual_spend / planned_spend) * 100
        else:
            pacing_percentage = 0

        # Determine pacing status
        if pacing_percentage >= 110:
            status = PacingStatus.AHEAD
        elif pacing_percentage >= 90:
            status = PacingStatus.ON_TRACK
        else:
            status = PacingStatus.BEHIND

        # Calculate additional metrics
        metrics = {
            'ctr': self._calculate_ctr(pacing_data.get('clicks', 0), pacing_data.get('impressions', 0)),
            'cpc': self._calculate_cpc(pacing_data.get('clicks', 0), actual_spend),
            'conversion_rate': self._calculate_conversion_rate(pacing_data.get('conversions', 0), pacing_data.get('clicks', 0)),
            'pacing_percentage': pacing_percentage
        }

        # Create or update pacing record
        pacing = CampaignPacing(
            media_plan_id=plan_id,
            date=datetime.utcnow(),
            planned_spend=planned_spend,
            actual_spend=actual_spend,
            impressions=pacing_data.get('impressions', 0),
            clicks=pacing_data.get('clicks', 0),
            conversions=pacing_data.get('conversions', 0),
            pacing_status=status,
            metrics=metrics
        )

        self.db.add(pacing)
        self.db.commit()
        self.db.refresh(pacing)
        return pacing

    def get_campaign_pacing(self, plan_id: int, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        pacing_data = self.db.query(CampaignPacing).filter(
            CampaignPacing.media_plan_id == plan_id,
            CampaignPacing.date.between(start_date, end_date)
        ).order_by(CampaignPacing.date).all()

        return [self._format_pacing_data(p) for p in pacing_data]

    def export_daily_metrics(self, plan_id: int, start_date: datetime, end_date: datetime, format: str = 'csv') -> bytes:
        pacing_data = self.get_campaign_pacing(plan_id, start_date, end_date)
        df = pd.DataFrame(pacing_data)

        if format.lower() == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format.lower() == 'excel':
            return df.to_excel(index=False).encode('utf-8')
        elif format.lower() == 'json':
            return json.dumps(pacing_data).encode('utf-8')
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_pacing_summary(self, plan_id: int) -> Dict[str, Any]:
        plan = self.db.query(MediaPlan).filter(MediaPlan.id == plan_id).first()
        if not plan:
            return {"error": "Media plan not found"}

        # Get latest pacing data
        latest_pacing = self.db.query(CampaignPacing).filter(
            CampaignPacing.media_plan_id == plan_id
        ).order_by(CampaignPacing.date.desc()).first()

        if not latest_pacing:
            return {"error": "No pacing data available"}

        # Calculate overall metrics
        total_planned = plan.budget
        total_actual = latest_pacing.actual_spend
        pacing_percentage = (total_actual / total_planned * 100) if total_planned > 0 else 0

        return {
            "plan_name": plan.name,
            "total_budget": total_planned,
            "spent_to_date": total_actual,
            "pacing_percentage": pacing_percentage,
            "current_status": latest_pacing.pacing_status.value,
            "latest_metrics": latest_pacing.metrics,
            "last_updated": latest_pacing.updated_at
        }

    def _calculate_ctr(self, clicks: int, impressions: int) -> float:
        return (clicks / impressions * 100) if impressions > 0 else 0

    def _calculate_cpc(self, clicks: int, spend: float) -> float:
        return spend / clicks if clicks > 0 else 0

    def _calculate_conversion_rate(self, conversions: int, clicks: int) -> float:
        return (conversions / clicks * 100) if clicks > 0 else 0

    def _format_pacing_data(self, pacing: CampaignPacing) -> Dict[str, Any]:
        return {
            "date": pacing.date.isoformat(),
            "planned_spend": pacing.planned_spend,
            "actual_spend": pacing.actual_spend,
            "impressions": pacing.impressions,
            "clicks": pacing.clicks,
            "conversions": pacing.conversions,
            "pacing_status": pacing.pacing_status.value,
            "metrics": pacing.metrics
        } 