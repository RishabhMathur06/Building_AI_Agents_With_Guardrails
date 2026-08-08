def validate_trade_action(action: dict, market_data: dict) -> dict:
    """
    Validates a trade action against enterprise trading policies.
    
    Args:
        action (dict): Contains 'type' (BUY/SELL), 'quantity', 'price', and 'ticker'.
        market_data (dict): Contains 'price_change_pct' and 'exchange'.
        
    Returns:
        dict: {'is_valid': bool, 'reason': str}
    """
    # Policy 1: No single trade order can exceed $10,000
    order_value = action.get('quantity', 0) * action.get('price', 0)
    if order_value > 10000:
        return {
            "is_valid": False,
            "reason": f"Order value ${order_value:,.2f} exceeds the $10,000 limit."
        }

    # Policy 2: SELL orders are not allowed if the stock price has dropped more than 5%
    if action.get('type') == 'SELL':
        price_change = market_data.get('price_change_pct', 0)
        if price_change < -5:
            return {
                "is_valid": False,
                "reason": f"SELL order rejected: price drop of {price_change}% exceeds 5% threshold."
            }

    # Policy 3: Only major exchange tickers are allowed
    major_exchanges = ["NYSE", "NASDAQ", "LSE", "JPX", "HKEX", "TSX"]
    if market_data.get('exchange') not in major_exchanges:
        return {
            "is_valid": False,
            "reason": f"Exchange '{market_data.get('exchange')}' is not a recognized major exchange."
        }

    return {
        "is_valid": True,
        "reason": "Trade action complies with all enterprise policies."
    }