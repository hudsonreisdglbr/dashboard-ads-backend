from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class GoogleAdsService:
    """
    Serviço para interagir com a API do Google Ads
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        developer_token: str,
        refresh_token: str,
        login_customer_id: Optional[str] = None
    ):
        """
        Inicializa o cliente do Google Ads com as credenciais fornecidas
        """
        self.client_config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "developer_token": developer_token,
            "refresh_token": refresh_token,
            "use_proto_plus": True  # Usar proto plus para melhor desempenho
        }
        
        if login_customer_id:
            self.client_config["login_customer_id"] = login_customer_id
            
        try:
            self.client = GoogleAdsClient.load_from_dict(self.client_config)
        except GoogleAdsException as ex:
            logger.error(f"Erro ao inicializar cliente Google Ads: {ex}")
            raise
    
    def get_campaigns(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Obtém a lista de campanhas para o ID de cliente fornecido
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Consulta para obter campanhas e métricas básicas
            query = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  campaign.start_date,
                  campaign.end_date,
                  campaign.advertising_channel_type,
                  metrics.impressions,
                  metrics.clicks,
                  metrics.ctr,
                  metrics.conversions,
                  metrics.cost_micros,
                  metrics.average_cpc,
                  metrics.average_cpa,
                  metrics.average_cpm,
                  metrics.cost_per_conversion
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                ORDER BY campaign.name
            """
            
            # Executar a consulta
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Processar os resultados
            campaigns = []
            for row in response:
                campaign = row.campaign
                metrics = row.metrics
                
                # Converter micros para unidades monetárias reais
                cost = metrics.cost_micros / 1000000.0
                cpc = metrics.average_cpc / 1000000.0 if metrics.average_cpc else 0
                cpa = metrics.average_cpa / 1000000.0 if metrics.average_cpa else 0
                cpm = metrics.average_cpm / 1000000.0 if metrics.average_cpm else 0
                
                # Calcular ROAS (se houver conversões e custo)
                roas = 0
                if metrics.conversions > 0 and cost > 0:
                    # Valor estimado por conversão (exemplo)
                    estimated_conversion_value = 100  # Valor fictício, idealmente viria dos dados
                    roas = (metrics.conversions * estimated_conversion_value) / cost
                
                campaigns.append({
                    "id": campaign.id,
                    "name": campaign.name,
                    "status": str(campaign.status).replace("CampaignStatus.", ""),
                    "channel": str(campaign.advertising_channel_type).replace("AdvertisingChannelType.", ""),
                    "start_date": campaign.start_date,
                    "end_date": campaign.end_date,
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "ctr": metrics.ctr,
                    "conversions": metrics.conversions,
                    "spend": cost,
                    "cpc": cpc,
                    "cpa": cpa,
                    "cpm": cpm,
                    "roas": roas
                })
            
            return campaigns
            
        except GoogleAdsException as ex:
            logger.error(f"Erro ao obter campanhas do Google Ads: {ex}")
            for error in ex.failure.errors:
                logger.error(f"\tError with message: {error.message}")
                logger.error(f"\tError code: {error.error_code}")
                logger.error(f"\tError location: {error.location}")
            raise
    
    def get_ad_groups(self, customer_id: str, campaign_id: str) -> List[Dict[str, Any]]:
        """
        Obtém os grupos de anúncios para uma campanha específica
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Consulta para obter grupos de anúncios
            query = f"""
                SELECT
                  ad_group.id,
                  ad_group.name,
                  ad_group.status,
                  metrics.impressions,
                  metrics.clicks,
                  metrics.ctr,
                  metrics.conversions,
                  metrics.cost_micros
                FROM ad_group
                WHERE ad_group.campaign.id = {campaign_id}
                ORDER BY ad_group.name
            """
            
            # Executar a consulta
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Processar os resultados
            ad_groups = []
            for row in response:
                ad_group = row.ad_group
                metrics = row.metrics
                
                # Converter micros para unidades monetárias reais
                cost = metrics.cost_micros / 1000000.0
                
                ad_groups.append({
                    "id": ad_group.id,
                    "name": ad_group.name,
                    "status": str(ad_group.status).replace("AdGroupStatus.", ""),
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "ctr": metrics.ctr,
                    "conversions": metrics.conversions,
                    "spend": cost
                })
            
            return ad_groups
            
        except GoogleAdsException as ex:
            logger.error(f"Erro ao obter grupos de anúncios do Google Ads: {ex}")
            raise
    
    def get_ads(self, customer_id: str, ad_group_id: str) -> List[Dict[str, Any]]:
        """
        Obtém os anúncios para um grupo de anúncios específico
        """
        try:
            ga_service = self.client.get_service("GoogleAdsService")
            
            # Consulta para obter anúncios
            query = f"""
                SELECT
                  ad_group_ad.ad.id,
                  ad_group_ad.ad.name,
                  ad_group_ad.ad.final_urls,
                  ad_group_ad.status,
                  ad_group_ad.ad.image_ad.image_url,
                  ad_group_ad.ad.text_ad.headline,
                  ad_group_ad.ad.text_ad.description1,
                  ad_group_ad.ad.text_ad.description2,
                  metrics.impressions,
                  metrics.clicks,
                  metrics.ctr,
                  metrics.conversions,
                  metrics.cost_micros
                FROM ad_group_ad
                WHERE ad_group_ad.ad_group.id = {ad_group_id}
                ORDER BY ad_group_ad.ad.name
            """
            
            # Executar a consulta
            response = ga_service.search(customer_id=customer_id, query=query)
            
            # Processar os resultados
            ads = []
            for row in response:
                ad_group_ad = row.ad_group_ad
                ad = ad_group_ad.ad
                metrics = row.metrics
                
                # Converter micros para unidades monetárias reais
                cost = metrics.cost_micros / 1000000.0
                
                # Determinar o tipo de anúncio e obter a URL da imagem, se disponível
                thumbnail_url = None
                if hasattr(ad, 'image_ad') and ad.image_ad.image_url:
                    thumbnail_url = ad.image_ad.image_url
                
                # Obter URL final do anúncio
                final_url = ad.final_urls[0] if ad.final_urls else None
                
                ads.append({
                    "id": ad.id,
                    "name": ad.name,
                    "status": str(ad_group_ad.status).replace("AdGroupAdStatus.", ""),
                    "thumbnail_url": thumbnail_url,
                    "final_url": final_url,
                    "impressions": metrics.impressions,
                    "clicks": metrics.clicks,
                    "ctr": metrics.ctr,
                    "conversions": metrics.conversions,
                    "spend": cost
                })
            
            return ads
            
        except GoogleAdsException as ex:
            logger.error(f"Erro ao obter anúncios do Google Ads: {ex}")
            raise
