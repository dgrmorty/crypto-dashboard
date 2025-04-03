import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import pandas as pd
from sklearn.linear_model import LinearRegression

app = FastAPI()

# Разрешаем CORS для клиента
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Кеширование данных (чтобы не спамить CoinGecko)
CRYPTO_CACHE = {}

def get_crypto_data(crypto: str):
    if crypto in CRYPTO_CACHE:
        return CRYPTO_CACHE[crypto]
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    url = f"https://api.coingecko.com/api/v3/coins/{crypto}/market_chart/range?vs_currency=usd&from={int(start_date.timestamp())}&to={int(end_date.timestamp())}"
    
    response = requests.get(url)
    data = response.json()
    CRYPTO_CACHE[crypto] = data['prices']
    return data['prices']

def predict_trend(prices):
    df = pd.DataFrame(prices, columns=['timestamp', 'price'])
    df['day'] = (df['timestamp'] - df['timestamp'].min()) / (1000 * 3600 * 24)
    
    model = LinearRegression()
    model.fit(df[['day']], df['price'])
    df['predicted_price'] = model.predict(df[['day']])
    
    return df

@app.get("/predict/{crypto}")
async def get_prediction(crypto: str):
    try:
        prices = get_crypto_data(crypto)
        df = predict_trend(prices)
        
        return {
            "dates": [datetime.fromtimestamp(ts // 1000).strftime("%Y-%m-%d") for ts in df['timestamp']],
            "prices": df["price"].tolist(),
            "predictions": df["predicted_price"].tolist()
        }
    except Exception as e:
        return {"error": str(e)}