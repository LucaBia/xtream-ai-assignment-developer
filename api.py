from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)