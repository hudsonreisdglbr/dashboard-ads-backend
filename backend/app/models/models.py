from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    
    # Relacionamentos
    google_ads_accounts = relationship("GoogleAdsAccount", back_populates="user")
    meta_ads_accounts = relationship("MetaAdsAccount", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")

class GoogleAdsAccount(Base):
    __tablename__ = "google_ads_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)
    name = Column(String)
    refresh_token = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relacionamentos
    user = relationship("User", back_populates="google_ads_accounts")
    campaigns = relationship("Campaign", back_populates="google_ads_account")

class MetaAdsAccount(Base):
    __tablename__ = "meta_ads_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, index=True)
    name = Column(String)
    access_token = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relacionamentos
    user = relationship("User", back_populates="meta_ads_accounts")
    campaigns = relationship("Campaign", back_populates="meta_ads_account")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String, index=True)
    name = Column(String, index=True)
    status = Column(String)  # active, paused, removed
    channel = Column(String)  # google, meta
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    total_investment = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"))
    google_ads_account_id = Column(Integer, ForeignKey("google_ads_accounts.id"), nullable=True)
    meta_ads_account_id = Column(Integer, ForeignKey("meta_ads_accounts.id"), nullable=True)
    
    # Relacionamentos
    user = relationship("User", back_populates="campaigns")
    google_ads_account = relationship("GoogleAdsAccount", back_populates="campaigns")
    meta_ads_account = relationship("MetaAdsAccount", back_populates="campaigns")
    ads = relationship("Ad", back_populates="campaign")
    metrics = relationship("CampaignMetric", back_populates="campaign")

class Ad(Base):
    __tablename__ = "ads"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(String, index=True)
    name = Column(String)
    ad_group = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    ad_link = Column(String, nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    # Relacionamentos
    campaign = relationship("Campaign", back_populates="ads")
    metrics = relationship("AdMetric", back_populates="ad")

class CampaignMetric(Base):
    __tablename__ = "campaign_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    cpc = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    spend = Column(Float, default=0.0)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    
    # Relacionamentos
    campaign = relationship("Campaign", back_populates="metrics")

class AdMetric(Base):
    __tablename__ = "ad_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    ctr = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    cpc = Column(Float, default=0.0)
    cpa = Column(Float, default=0.0)
    cpm = Column(Float, default=0.0)
    roas = Column(Float, default=0.0)
    spend = Column(Float, default=0.0)
    ad_id = Column(Integer, ForeignKey("ads.id"))
    
    # Relacionamentos
    ad = relationship("Ad", back_populates="metrics")
