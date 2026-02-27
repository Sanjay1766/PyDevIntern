def validate_symbol(symbol: str) -> bool:
    return symbol.isalnum() and symbol.isupper()

def validate_side(side: str) -> bool:
    return side in ('BUY', 'SELL')

def validate_order_type(order_type: str) -> bool:
    return order_type in ('MARKET', 'LIMIT')

def validate_quantity(quantity: float) -> bool:
    return quantity > 0

def validate_price(price: float) -> bool:
    return price > 0
