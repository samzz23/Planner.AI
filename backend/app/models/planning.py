from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime
import enum

class PacingStatus(enum.Enum):
    AHEAD = "ahead"
    ON_TRACK = "on_track"
    BEHIND = "behind"
    COMPLETED = "completed"

class MediaPlan(Base):
    __tablename__ = "media_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    budget = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    channels = relationship("ChannelAllocation", back_populates="media_plan")
    metrics = relationship("PerformanceMetric", back_populates="media_plan")
    scenarios = relationship("Scenario", back_populates="media_plan")
    pacing = relationship("CampaignPacing", back_populates="media_plan")

class ChannelAllocation(Base):
    __tablename__ = "channel_allocations"

    id = Column(Integer, primary_key=True, index=True)
    media_plan_id = Column(Integer, ForeignKey("media_plans.id"))
    channel_name = Column(String)
    budget_allocation = Column(Float)
    target_audience = Column(JSON)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media_plan = relationship("MediaPlan", back_populates="channels")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    media_plan_id = Column(Integer, ForeignKey("media_plans.id"))
    metric_name = Column(String)
    value = Column(Float)
    target = Column(Float)
    actual = Column(Float)
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media_plan = relationship("MediaPlan", back_populates="metrics")

class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    media_plan_id = Column(Integer, ForeignKey("media_plans.id"))
    name = Column(String)
    description = Column(String)
    assumptions = Column(JSON)
    results = Column(JSON)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media_plan = relationship("MediaPlan", back_populates="scenarios")

class CampaignPacing(Base):
    __tablename__ = "campaign_pacing"

    id = Column(Integer, primary_key=True, index=True)
    media_plan_id = Column(Integer, ForeignKey("media_plans.id"))
    date = Column(DateTime, index=True)
    planned_spend = Column(Float)
    actual_spend = Column(Float)
    impressions = Column(Integer)
    clicks = Column(Integer)
    conversions = Column(Integer)
    pacing_status = Column(Enum(PacingStatus))
    metrics = Column(JSON)  # Additional metrics like CTR, CPC, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    media_plan = relationship("MediaPlan", back_populates="pacing")

class HistoricalData(Base):
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    data_type = Column(String)  # sales, spend, traffic, etc.
    date = Column(DateTime)
    value = Column(Float)
    channel = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 