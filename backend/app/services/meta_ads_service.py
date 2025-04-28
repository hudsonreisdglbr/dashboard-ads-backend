from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.exceptions import FacebookRequestError
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MetaAdsService:
    """
    Serviço para interagir com a API do Meta Ads (Facebook/Instagram)
    """
    
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        access_token: str
    ):
        """
        Inicializa a API do Meta Ads com as credenciais fornecidas
        """
        try:
            FacebookAdsApi.init(app_id=app_id, app_secret=app_secret, access_token=access_token)
        except Exception as e:
            logger.error(f"Erro ao inicializar Meta Ads API: {e}")
            raise
            
    def get_campaigns(self, ad_account_id: str) -> List[Dict[str, Any]]:
        """
        Obtém a lista de campanhas para o ID da conta de anúncios fornecido
        """
        try:
            account = AdAccount(f"act_{ad_account_id}")
            
            # Campos a serem buscados para campanhas e métricas
            fields = [
                Campaign.Field.id,
                Campaign.Field.name,
                Campaign.Field.status,
                Campaign.Field.start_time,
                Campaign.Field.stop_time,
                Campaign.Field.objective,
                Campaign.Field.spend,
                Campaign.Field.impressions,
                Campaign.Field.clicks,
                Campaign.Field.ctr,
                Campaign.Field.cpc,
                Campaign.Field.cpm,
                Campaign.Field.cpp, # Cost per result (similar to CPA)
                Campaign.Field.actions, # Conversions
                Campaign.Field.roas, # Return on Ad Spend
            ]
            params = {
                # Filtrar por status (opcional)
                # 'filtering': [{'field': 'campaign.effective_status', 'operator': 'IN', 'value': ['ACTIVE', 'PAUSED']}],
                'date_preset': 'last_30d', # Período das métricas
                'level': 'campaign',
            }
            
            # Obter insights (métricas)
            insights = account.get_insights(fields=fields, params=params)
            
            # Processar os resultados
            campaigns = []
            for insight in insights:
                # Extrair conversões (exemplo: compras)
                conversions = 0
                if insight.get(Campaign.Field.actions):
                    for action in insight[Campaign.Field.actions]:
                        if action["action_type"] == "purchase": # Ajustar conforme o tipo de conversão desejado
                            conversions = int(action["value"])
                            break
                
                # Extrair ROAS (se disponível)
                roas_value = 0.0
                if insight.get(Campaign.Field.roas):
                     for roas_item in insight[Campaign.Field.roas]:
                         if roas_item["action_type"] == "purchase_roas": # Ajustar conforme o tipo de ROAS desejado
                             roas_value = float(roas_item["value"])
                             break
                
                campaigns.append({
                    "id": insight[Campaign.Field.id],
                    "name": insight[Campaign.Field.name],
                    "status": insight[Campaign.Field.status],
                    "channel": "meta", # Definido como Meta
                    "start_date": insight.get(Campaign.Field.start_time),
                    "end_date": insight.get(Campaign.Field.stop_time),
                    "impressions": int(insight.get(Campaign.Field.impressions, 0)),
                    "clicks": int(insight.get(Campaign.Field.clicks, 0)),
                    "ctr": float(insight.get(Campaign.Field.ctr, 0.0)),
                    "conversions": conversions,
                    "spend": float(insight.get(Campaign.Field.spend, 0.0)),
                    "cpc": float(insight.get(Campaign.Field.cpc, 0.0)),
                    "cpa": float(insight.get(Campaign.Field.cpp, 0.0)), # Usando CPP como CPA
                    "cpm": float(insight.get(Campaign.Field.cpm, 0.0)),
                    "roas": roas_value
                })
            
            return campaigns
            
        except FacebookRequestError as e:
            logger.error(f"Erro ao obter campanhas do Meta Ads: {e}")
            logger.error(f"Error code: {e.api_error_code()}")
            logger.error(f"Error message: {e.api_error_message()}")
            raise
            
    def get_ads(self, ad_account_id: str, campaign_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtém os anúncios (e seus criativos) para uma conta ou campanha específica
        """
        try:
            account = AdAccount(f"act_{ad_account_id}")
            
            # Campos para anúncios e criativos
            ad_fields = [
                Ad.Field.id,
                Ad.Field.name,
                Ad.Field.status,
                Ad.Field.campaign_id,
                Ad.Field.adset_id,
                Ad.Field.creative,
            ]
            creative_fields = [
                AdCreative.Field.id,
                AdCreative.Field.name,
                AdCreative.Field.thumbnail_url,
                AdCreative.Field.object_story_spec, # Para obter link e imagem/vídeo
                AdCreative.Field.image_url,
                AdCreative.Field.video_id,
            ]
            insight_fields = [
                Ad.Field.impressions,
                Ad.Field.clicks,
                Ad.Field.ctr,
                Ad.Field.spend,
                Ad.Field.actions, # Conversões
            ]
            
            params = {
                'date_preset': 'last_30d',
                'level': 'ad',
                'filtering': [],
            }
            if campaign_id:
                params['filtering'].append({'field': 'ad.campaign_id', 'operator': 'EQUAL', 'value': campaign_id})
            
            # Obter insights dos anúncios
            insights = account.get_insights(fields=insight_fields + ad_fields, params=params)
            
            ads_data = []
            for insight in insights:
                creative_id = insight.get(Ad.Field.creative, {}).get("id")
                thumbnail_url = None
                ad_link = None
                
                # Buscar detalhes do criativo se existir
                if creative_id:
                    try:
                        creative = AdCreative(creative_id).api_get(fields=creative_fields)
                        thumbnail_url = creative.get(AdCreative.Field.thumbnail_url) or creative.get(AdCreative.Field.image_url)
                        
                        # Tentar obter o link do object_story_spec
                        object_story_spec = creative.get(AdCreative.Field.object_story_spec)
                        if object_story_spec:
                            if 'link_data' in object_story_spec and 'link' in object_story_spec['link_data']:
                                ad_link = object_story_spec['link_data']['link']
                            elif 'video_data' in object_story_spec and 'call_to_action' in object_story_spec['video_data'] and 'value' in object_story_spec['video_data']['call_to_action'] and 'link' in object_story_spec['video_data']['call_to_action']['value']:
                                ad_link = object_story_spec['video_data']['call_to_action']['value']['link']
                                
                    except FacebookRequestError as creative_error:
                        logger.warning(f"Erro ao buscar criativo {creative_id}: {creative_error}")
                
                # Extrair conversões
                conversions = 0
                if insight.get(Ad.Field.actions):
                    for action in insight[Ad.Field.actions]:
                        if action["action_type"] == "purchase": # Ajustar conforme necessário
                            conversions = int(action["value"])
                            break
                            
                ads_data.append({
                    "id": insight[Ad.Field.id],
                    "name": insight[Ad.Field.name],
                    "status": insight[Ad.Field.status],
                    "campaign_id": insight[Ad.Field.campaign_id],
                    "adset_id": insight.get(Ad.Field.adset_id),
                    "thumbnail_url": thumbnail_url,
                    "ad_link": ad_link,
                    "impressions": int(insight.get(Ad.Field.impressions, 0)),
                    "clicks": int(insight.get(Ad.Field.clicks, 0)),
                    "ctr": float(insight.get(Ad.Field.ctr, 0.0)),
                    "spend": float(insight.get(Ad.Field.spend, 0.0)),
                    "conversions": conversions,
                })
                
            return ads_data

        except FacebookRequestError as e:
            logger.error(f"Erro ao obter anúncios do Meta Ads: {e}")
            logger.error(f"Error code: {e.api_error_code()}")
            logger.error(f"Error message: {e.api_error_message()}")
            raise
