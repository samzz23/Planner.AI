from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from app.db.session import get_db
from app.services.planning_service import PlanningService
from app.services.campaign_service import CampaignService
from app.models.planning import MediaPlan, ChannelAllocation, Scenario

router = APIRouter()

@router.post("/plans/", response_model=Dict[str, Any])
def create_media_plan(plan_data: Dict[str, Any], db: Session = Depends(get_db)):
    service = PlanningService(db)
    return service.create_media_plan(plan_data)

@router.get("/plans/{plan_id}", response_model=Dict[str, Any])
def get_media_plan(plan_id: int, db: Session = Depends(get_db)):
    service = PlanningService(db)
    plan = service.get_media_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Media plan not found")
    return plan

@router.post("/plans/{plan_id}/channels/", response_model=Dict[str, Any])
def add_channel_allocation(plan_id: int, channel_data: Dict[str, Any], db: Session = Depends(get_db)):
    service = PlanningService(db)
    return service.update_channel_allocation(plan_id, channel_data)

@router.get("/analysis/historical/", response_model=Dict[str, Any])
def analyze_historical_data(
    data_type: str,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    service = PlanningService(db)
    return service.analyze_historical_data(data_type, start_date, end_date)

@router.get("/analysis/forecast/", response_model=Dict[str, Any])
def generate_forecast(
    data_type: str,
    forecast_periods: int,
    db: Session = Depends(get_db)
):
    service = PlanningService(db)
    return service.generate_forecast(data_type, forecast_periods)

@router.post("/plans/{plan_id}/scenarios/", response_model=Dict[str, Any])
def create_scenario(plan_id: int, scenario_data: Dict[str, Any], db: Session = Depends(get_db)):
    service = PlanningService(db)
    return service.create_scenario(plan_id, scenario_data)

# Campaign Pacing Routes
@router.post("/plans/{plan_id}/pacing/", response_model=Dict[str, Any])
def update_campaign_pacing(plan_id: int, pacing_data: Dict[str, Any], db: Session = Depends(get_db)):
    service = CampaignService(db)
    return service.update_campaign_pacing(plan_id, pacing_data)

@router.get("/plans/{plan_id}/pacing/", response_model=List[Dict[str, Any]])
def get_campaign_pacing(
    plan_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    service = CampaignService(db)
    return service.get_campaign_pacing(plan_id, start_date, end_date)

@router.get("/plans/{plan_id}/pacing/summary/", response_model=Dict[str, Any])
def get_pacing_summary(plan_id: int, db: Session = Depends(get_db)):
    service = CampaignService(db)
    return service.get_pacing_summary(plan_id)

@router.get("/plans/{plan_id}/metrics/export/")
def export_daily_metrics(
    plan_id: int,
    start_date: datetime,
    end_date: datetime,
    format: str = "csv",
    db: Session = Depends(get_db)
):
    service = CampaignService(db)
    try:
        data = service.export_daily_metrics(plan_id, start_date, end_date, format)
        
        # Set appropriate headers based on format
        headers = {
            "csv": "text/csv",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "json": "application/json"
        }
        
        return Response(
            content=data,
            media_type=headers.get(format.lower(), "text/csv"),
            headers={
                "Content-Disposition": f"attachment; filename=campaign_metrics_{plan_id}_{start_date.date()}_{end_date.date()}.{format}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) 