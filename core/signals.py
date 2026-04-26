def detect_price_signal(previous_price, current_price):
    if previous_price is None:
        return None
    
    change=((current_price-previous_price)/previous_price)*100

    if change<=-2:
        return("price_drop", change)
    if change>=2:
        return("price_rise", change)
    
    return None

def detect_volume_spike(previous_volume, current_volume):
    if previous_volume is None:
        return None
    
    change=((current_volume-previous_volume)/previous_volume)*100

    if change>=10:
        return("volume_spike", change)
    
    return None

def detect_volatility(prices):
    if len(prices)<5:
        return None
    
    max_price=max(prices)
    min_price=min(prices)

    change=((max_price-min_price)/min_price)*100

    if change>=3:
        return("high_volatility", change)
    
    return None