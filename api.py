from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import uvicorn
import asyncio


app = FastAPI(title="Xtream Diamond Price Prediction API")

class Diamond(BaseModel):
    carat: float
    cut: str
    color: str
    clarity: str
    depth: float = 0.0
    table: float = 0.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

class SampleRequest(BaseModel):
    cut: str
    color: str
    clarity: str
    carat: float
    n_samples: int = 5


try:
    data_url = "https://raw.githubusercontent.com/xtreamsrl/xtream-ai-assignment-engineer/main/datasets/diamonds/diamonds.csv"
    data = pd.read_csv(data_url)
    data = data[(data.x * data.y * data.z != 0) & (data.price > 0)]
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Dataset file not found")

try:
    model = joblib.load("./notebooks/models/XGBoost/03-07-2024-00-53-12/model.joblib")
except FileNotFoundError:
    raise HTTPException(status_code=500, detail="Model file not found")

def prepare_features(diamond: Diamond):
    data = {
        'carat': [diamond.carat],
        'depth': [diamond.depth],
        'table': [diamond.table],
        'x': [diamond.x],
        'y': [diamond.y],
        'z': [diamond.z],
        'cut': [diamond.cut],
        'color': [diamond.color],
        'clarity': [diamond.clarity]
    }
    df = pd.DataFrame(data)
    df = pd.get_dummies(df, columns=['cut', 'color', 'clarity'], drop_first=False)
    
    expected_features = model.get_booster().feature_names
    missing_cols = set(expected_features) - set(df.columns)
    # print(missing_cols)
    
    for i in missing_cols:
        df[i] = 0
    df = df[expected_features]

    return df

@app.post("/predict/")
async def predict_price(diamond: Diamond):
    features = prepare_features(diamond)
    prediction = model.predict(features)
    prediction = prediction[0].item()
    return {"predicted_price": prediction}

@app.post("/fetch_samples/")
async def fetch_samples(request: SampleRequest):
    similar_diamonds = data[(data['cut'] == request.cut) & (data['color'] == request.color) & (data['clarity'] == request.clarity)]
    
    similar_diamonds['carat_diff'] = np.abs(similar_diamonds['carat'] - request.carat)
    closest_diamonds = similar_diamonds.nsmallest(request.n_samples, 'carat_diff')
    
    result = closest_diamonds[['carat', 'cut', 'color', 'clarity', 'depth', 'table', 'x', 'y', 'z', 'price']]

    return result.to_dict(orient='records')

@app.get("/")
async def read_root():
    return {"message": "Ciao Xtreamer 🚀"}

async def startup_event():
    print("Starting server ⭐️")

async def shutdown_event():
    print("Arriverderci Xtreamer☕️")

app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)


if __name__ == "__main__":
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    
    loop = asyncio.get_event_loop()
    
    try:
        loop.run_until_complete(server.serve())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()