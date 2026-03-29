"""Profit margin calculator."""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ProfitCalculator:
    """Calculates profit margin for arbitrage opportunities."""

    # eBay fees
    EBAY_FINAL_VALUE_FEE = 0.129  # 12.9% FVFF for most categories

    # PayPal fees (when paid via eBay)
    PAYPAL_TRANSACTION_FEE = 0.029  # 2.9%
    PAYPAL_GATEWAY_FEE = 0.30  # $0.30 per transaction

    # Additional costs
    PACKAGING_COST = 0.50  # Packaging materials
    SHIPPING_SCALE_FEE = 0.01  # Minor shipping-related fees

    # Profit thresholds
    MIN_PROFIT_MARGIN_PERCENT = 0.30  # 30%
    MIN_PROFIT_DOLLAR = 10  # Minimum $10 profit

    def calculate_ebay_fees(self, selling_price: float) -> Dict:
        """Calculate all eBay-related fees.
        
        Args:
            selling_price: Price item sells for on eBay
            
        Returns:
            Dict with fee breakdown
        """
        # Final value fee
        fvff = selling_price * self.EBAY_FINAL_VALUE_FEE

        # PayPal fees
        paypal_percent_fee = selling_price * self.PAYPAL_TRANSACTION_FEE
        paypal_fixed_fee = self.PAYPAL_GATEWAY_FEE
        paypal_total = paypal_percent_fee + paypal_fixed_fee

        # Other costs
        packaging = self.PACKAGING_COST
        shipping_fees = self.SHIPPING_SCALE_FEE

        total_fees = fvff + paypal_total + packaging + shipping_fees

        return {
            'ebay_fvff': round(fvff, 2),
            'paypal_percent': round(paypal_percent_fee, 2),
            'paypal_fixed': round(paypal_fixed_fee, 2),
            'paypal_total': round(paypal_total, 2),
            'packaging': round(packaging, 2),
            'shipping_scale_fee': round(shipping_fees, 2),
            'total_fees': round(total_fees, 2),
        }

    def calculate_profit(
        self,
        ebay_selling_price: float,
        landed_cost: float,
        quantity: int = 1,
    ) -> Dict:
        """Calculate profit for an arbitrage opportunity.
        
        Args:
            ebay_selling_price: Price item sells for on eBay
            landed_cost: Total cost to get item to your door (from shipping calculator)
            quantity: Quantity to calculate for
            
        Returns:
            Dict with profit analysis
        """
        # Get all fees
        fees = self.calculate_ebay_fees(ebay_selling_price)

        # Calculate profit per unit
        revenue = ebay_selling_price
        cost_of_goods = landed_cost
        selling_fees = fees['total_fees']

        gross_profit = revenue - cost_of_goods
        net_profit = gross_profit - selling_fees

        profit_margin_percent = (net_profit / revenue) if revenue > 0 else 0
        profit_margin_dollar = net_profit

        # For multiple units
        total_revenue = revenue * quantity
        total_cost = cost_of_goods * quantity
        total_fees = selling_fees * quantity
        total_profit = net_profit * quantity

        result = {
            'per_unit': {
                'ebay_selling_price': round(ebay_selling_price, 2),
                'landed_cost': round(cost_of_goods, 2),
                'selling_fees': round(selling_fees, 2),
                'gross_profit': round(gross_profit, 2),
                'net_profit': round(net_profit, 2),
                'profit_margin_percent': round(profit_margin_percent * 100, 2),
                'profit_margin_ratio': round(profit_margin_percent, 3),
            },
            'for_quantity': {
                'quantity': quantity,
                'total_revenue': round(total_revenue, 2),
                'total_cost': round(total_cost, 2),
                'total_fees': round(total_fees, 2),
                'total_profit': round(total_profit, 2),
            },
            'fees_breakdown': fees,
            'profitability': {
                'is_profitable': net_profit > self.MIN_PROFIT_DOLLAR,
                'meets_percent_target': profit_margin_percent >= self.MIN_PROFIT_MARGIN_PERCENT,
                'meets_dollar_target': net_profit >= self.MIN_PROFIT_DOLLAR,
            },
        }

        return result

    def evaluate_opportunity(
        self,
        product_name: str,
        ebay_selling_price: float,
        ebay_demand_score: float,
        source_platform: str,
        source_price: float,
        shipping_data: Dict,
        quantity: int = 1,
    ) -> Dict:
        """Comprehensive evaluation of an arbitrage opportunity.
        
        Args:
            product_name: Product name
            ebay_selling_price: eBay selling price
            ebay_demand_score: Demand validation score (0-100)
            source_platform: Platform where product is sourced (Taobao, etc)
            source_price: Price on source platform
            shipping_data: Shipping calculation data
            quantity: Quantity to evaluate
            
        Returns:
            Comprehensive opportunity evaluation
        """
        landed_cost = shipping_data.get('total_cost_usd', source_price)
        profit_analysis = self.calculate_profit(
            ebay_selling_price,
            landed_cost,
            quantity
        )

        # Determine overall opportunity quality
        profit_score = 0
        if profit_analysis['profitability']['meets_percent_target']:
            profit_score += 50
        if profit_analysis['profitability']['meets_dollar_target']:
            profit_score += 30
        if ebay_demand_score >= 70:
            profit_score += 20

        is_winner = (
            profit_analysis['profitability']['is_profitable'] and
            profit_analysis['profitability']['meets_percent_target'] and
            ebay_demand_score >= 50
        )

        return {
            'product_name': product_name,
            'source_platform': source_platform,
            'ebay_selling_price': round(ebay_selling_price, 2),
            'landed_cost': round(landed_cost, 2),
            'profit_per_unit': round(profit_analysis['per_unit']['net_profit'], 2),
            'profit_margin_percent': profit_analysis['per_unit']['profit_margin_percent'],
            'ebay_demand_score': round(ebay_demand_score, 2),
            'profit_score': profit_score,
            'overall_score': (profit_score + ebay_demand_score) / 2,
            'is_winner': is_winner,
            'quantity': quantity,
            'total_profit': round(profit_analysis['for_quantity']['total_profit'], 2),
            'profit_analysis': profit_analysis,
            'shipping_details': shipping_data,
        }
