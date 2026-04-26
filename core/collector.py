import requests

ASSETS=[
    "bitcoin", "ethereum", "tether", "binancecoin", "solana",
    "ripple", "usd-coin", "cardano", "dogecoin", "tron",
    "polkadot", "polygon", "litecoin", "shiba-inu", "avalanche-2",
    "dai", "chainlink", "uniswap", "leo-token", "cosmos",
    "stellar", "monero", "ethereum-classic", "okb", "filecoin",
    "internet-computer", "aptos", "hedera-hashgraph", "vechain", "quant-network",
    "arbitrum", "optimism", "the-graph", "sandbox", "decentraland",
    "algorand", "flow", "tezos", "aave", "maker",
    "fantom", "theta-token", "eos", "axie-infinity", "neo",
    "kava", "zilliqa", "waves", "iota", "elrond-erd-2"
]

API_URL="https://api.coingecko.com/api/v3/simple/price"

def fetch_prices():
    params={
        "ids": ",".join(ASSETS),
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }

    response=requests.get(API_URL, params=params)
    data=response.json()

    results=[]

    for asset in ASSETS:
        if asset not in data:
            continue

        item=data[asset]

        results.append({
            "symbol": asset,
            "name": asset.capitalize(),
            "price": item["usd"],
            "market_cap": item.get("usd_market_cap"),
            "volume": item.get("usd_24h_vol"),
            "change_24h": item.get("usd_24h_change")
        })

    return results