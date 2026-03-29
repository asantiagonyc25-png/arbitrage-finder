"""Shipping cost calculator for various platforms and sources."""

import logging
from typing import Dict, Optional
import requests

logger = logging.getLogger(__name__)


class ShippingCalculator:
    """Calculates shipping costs for products from various sources."""

    # Estimated shipping rates (per kg, USD)
    SHIPPING_ROUTES = {
        'china_to_us': {
            'epacket': 2.50,  # Lighter items
            'registered_airmail': 3.00,
            'ems': 8.00,  # Faster
            'dhl': 12.00,
            'fedex': 15.00,
        },
        'japan_to_us': {
            'registered_airmail': 5.00,
            'ems': 12.00,
            'dhl': 15.00,
            'surface': 3.00,  # Very slow (1-3 months)
        },
    }

    # Service fees (as percentage of item price)
    SERVICE_FEES = {
        'mulebuy': 0.06,      # 6% fee
        'superbuy': 0.08,     # 8% fee
        'buyee': 0.085,       # 8.5% fee
        'zenmarket': 0.08,    # 8% fee
    }

    # Base fees (flat USD)
    BASE_FEES = {
        'mulebuy': 0.50,
        'superbuy': 1.00,
        'buyee': 0.50,
        'zenmarket': 1.50,
    }

    # Shipping method selection
    SHIPPING_METHODS = {
        'china': 'epacket',      # Most cost-effective for China
        'japan': 'registered_airmail',  # Most cost-effective for Japan
    }

    def estimate_package_weight(self, item_price: float, product_type: str = 'general') -> float:
        """Estimate package weight based on price (heuristic).
        
        Args:
            item_price: Item price in USD
            product_type: Type of product
            
        Returns:
            Estimated weight in kg
        """
        # Rough correlation: higher priced items tend to be heavier
        # This is a heuristic estimation
        if item_price < 10:
            return 0.3  # Small items: ~300g
        elif item_price < 30:
            return 0.5  # Medium items: ~500g
        elif item_price < 100:
            return 0.8  # Medium items: ~800g
        elif item_price < 300:
            return 1.2  # Larger items: ~1.2kg
        else:
            return min(2.0, item_price / 200)  # Rough estimate

    def calculate_china_shipping(
        self,
        item_price: float,
        source_platform: str,
        item_weight_kg: Optional[float] = None,
        service_provider: str = 'mulebuy',
    ) -> Dict:
        """Calculate total cost including shipping from Chinese marketplace.
        
        Args:
            item_price: Item price in CNY
            source_platform: Taobao, 1688, Alibaba
            item_weight_kg: Item weight in kg (estimated if not provided)
            service_provider: mulebuy or superbuy
            
        Returns:
            Dict with cost breakdown
        """
        if item_weight_kg is None:
            # Estimate weight - assume price is roughly in CNY, convert to rough USD for estimation
            item_price_usd = item_price / 7.0
            item_weight_kg = self.estimate_package_weight(item_price_usd)

        # Calculate costs
        result = {
            'source_platform': source_platform,
            'service_provider': service_provider,
            'item_price_cny': item_price,
            'item_price_usd': item_price / 7.0,
            'item_weight_kg': item_weight_kg,
            'currency': 'CNY',
        }

        # Service fees
        service_fee_percent = self.SERVICE_FEES.get(service_provider, 0.07)
        service_fee_amount = (item_price / 7.0) * service_fee_percent  # Fee on USD price
        result['service_fee_usd'] = round(service_fee_amount, 2)

        # Base fee
        base_fee = self.BASE_FEES.get(service_provider, 0.50)
        result['base_fee_usd'] = base_fee

        # Shipping cost
        shipping_method = self.SHIPPING_METHODS['china']
        shipping_rate = self.SHIPPING_ROUTES['china_to_us'][shipping_method]
        shipping_cost = shipping_rate * item_weight_kg
        result['shipping_cost_usd'] = round(min(shipping_cost, 25), 2)  # Cap at $25
        result['shipping_method'] = shipping_method

        # Import duties/taxes (rough estimate: 8-15% for items under $800)
        import_tax = (item_price / 7.0) * 0.10  # 10% estimate
        result['import_tax_usd'] = round(import_tax, 2)

        # Total landed cost
        total_cost = (
            result['item_price_usd'] +
            result['service_fee_usd'] +
            result['base_fee_usd'] +
            result['shipping_cost_usd'] +
            result['import_tax_usd']
        )
        result['total_cost_usd'] = round(total_cost, 2)

        return result

    def calculate_japan_shipping(
        self,
        item_price_jpy: float,
        source_platform: str,
        item_weight_kg: Optional[float] = None,
        service_provider: str = 'buyee',
    ) -> Dict:
        """Calculate total cost including shipping from Japanese marketplace.
        
        Args:
            item_price_jpy: Item price in JPY
            source_platform: Yahoo Auctions, Mercari JP
            item_weight_kg: Item weight in kg (estimated if not provided)
            service_provider: buyee or zenmarket
            
        Returns:
            Dict with cost breakdown
        """
        if item_weight_kg is None:
            item_price_usd = item_price_jpy / 150
            item_weight_kg = self.estimate_package_weight(item_price_usd)

        # Calculate costs
        result = {
            'source_platform': source_platform,
            'service_provider': service_provider,
            'item_price_jpy': item_price_jpy,
            'item_price_usd': item_price_jpy / 150,
            'item_weight_kg': item_weight_kg,
            'currency': 'JPY',
        }

        # Service fees
        service_fee_percent = self.SERVICE_FEES.get(service_provider, 0.08)
        service_fee_amount = result['item_price_usd'] * service_fee_percent
        result['service_fee_usd'] = round(service_fee_amount, 2)

        # Base fee
        base_fee = self.BASE_FEES.get(service_provider, 1.00)
        result['base_fee_usd'] = base_fee

        # Shipping cost
        shipping_method = self.SHIPPING_METHODS['japan']
        shipping_rate = self.SHIPPING_ROUTES['japan_to_us'][shipping_method]
        shipping_cost = shipping_rate * item_weight_kg
        result['shipping_cost_usd'] = round(min(shipping_cost, 30), 2)  # Cap at $30
        result['shipping_method'] = shipping_method

        # Import duties/taxes (lower for used items, higher for new)
        import_tax = result['item_price_usd'] * 0.08  # 8% estimate
        result['import_tax_usd'] = round(import_tax, 2)

        # Total landed cost
        total_cost = (
            result['item_price_usd'] +
            result['service_fee_usd'] +
            result['base_fee_usd'] +
            result['shipping_cost_usd'] +
            result['import_tax_usd']
        )
        result['total_cost_usd'] = round(total_cost, 2)

        return result

    def calculate_total_cost(
        self,
        source_data: Dict,
        item_weight_kg: Optional[float] = None,
    ) -> Dict:
        """Calculate total cost based on source marketplace data.
        
        Args:
            source_data: Dict from source marketplace finder (contains platform, price, etc)
            item_weight_kg: Optional weight in kg
            
        Returns:
            Dict with full cost breakdown
        """
        platform = source_data.get('platform', '')
        
        if platform in ['taobao', '1688']:
            return self.calculate_china_shipping(
                source_data.get('min_price_cny', source_data.get('min_price_usd', 0) * 7),
                platform,
                item_weight_kg,
                'mulebuy'
            )
        elif platform == 'alibaba':
            return self.calculate_china_shipping(
                source_data.get('min_price_usd', 0) * 7,
                platform,
                item_weight_kg,
                'superbuy'
            )
        elif platform in ['yahoo_auctions', 'mercari_japan']:
            price_jpy = source_data.get('min_price_usd', 0) * 150
            return self.calculate_japan_shipping(
                price_jpy,
                platform,
                item_weight_kg,
                'buyee' if platform == 'yahoo_auctions' else 'zenmarket'
            )
        else:
            logger.warning(f"Unknown platform: {platform}")
            return {}
