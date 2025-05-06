from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.planning import MediaPlan, ChannelAllocation, PerformanceMetric, Scenario, HistoricalData
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

class PlanningService:
    def __init__(self, db: Session):
        self.db = db

    def create_media_plan(self, data: Dict[str, Any]) -> MediaPlan:
        media_plan = MediaPlan(**data)
        self.db.add(media_plan)
        self.db.commit()
        self.db.refresh(media_plan)
        return media_plan

    def get_media_plan(self, plan_id: int) -> MediaPlan:
        return self.db.query(MediaPlan).filter(MediaPlan.id == plan_id).first()

    def update_channel_allocation(self, plan_id: int, channel_data: Dict[str, Any]) -> ChannelAllocation:
        allocation = ChannelAllocation(**channel_data, media_plan_id=plan_id)
        self.db.add(allocation)
        self.db.commit()
        self.db.refresh(allocation)
        return allocation

    def analyze_historical_data(self, data_type: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        historical_data = self.db.query(HistoricalData).filter(
            HistoricalData.data_type == data_type,
            HistoricalData.date.between(start_date, end_date)
        ).all()
        
        df = pd.DataFrame([{
            'date': h.date,
            'value': h.value,
            'channel': h.channel
        } for h in historical_data])
        
        if df.empty:
            return {"error": "No historical data found"}
        
        # Basic analysis
        analysis = {
            "total": df['value'].sum(),
            "average": df['value'].mean(),
            "trend": self._calculate_trend(df),
            "channel_performance": df.groupby('channel')['value'].agg(['sum', 'mean']).to_dict()
        }
        
        return analysis

    def generate_forecast(self, data_type: str, forecast_periods: int) -> Dict[str, Any]:
        historical_data = self.db.query(HistoricalData).filter(
            HistoricalData.data_type == data_type
        ).order_by(HistoricalData.date).all()
        
        if not historical_data:
            return {"error": "No historical data available for forecasting"}
        
        # Prepare data for forecasting
        df = pd.DataFrame([{
            'date': h.date,
            'value': h.value
        } for h in historical_data])
        
        # Simple linear regression forecast
        X = np.array(range(len(df))).reshape(-1, 1)
        y = df['value'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate forecast
        future_X = np.array(range(len(df), len(df) + forecast_periods)).reshape(-1, 1)
        forecast = model.predict(future_X)
        
        # Generate dates for forecast
        last_date = df['date'].max()
        forecast_dates = [last_date + timedelta(days=i+1) for i in range(forecast_periods)]
        
        return {
            "forecast": list(zip(forecast_dates, forecast.tolist())),
            "model_accuracy": model.score(X, y)
        }

    def create_scenario(self, plan_id: int, scenario_data: Dict[str, Any]) -> Scenario:
        scenario = Scenario(**scenario_data, media_plan_id=plan_id)
        self.db.add(scenario)
        self.db.commit()
        self.db.refresh(scenario)
        return scenario

    def _calculate_trend(self, df: pd.DataFrame) -> float:
        if len(df) < 2:
            return 0
        
        X = np.array(range(len(df))).reshape(-1, 1)
        y = df['value'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        return model.coef_[0]  # Return the slope of the trend line 