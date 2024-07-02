from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
import uvicorn

app = FastAPI(title="Xtream Diamond Price Prediction API")

def load_data(file):
    """
    Load and preprocess data from a CSV file.
    
    Parameters:
        file (str): URL or local path to the CSV file containing data.
    
    Returns:
        pd.DataFrame: Preprocessed DataFrame with one-hot encoded categorical variables and filtered invalid entries.
    """
    diamonds = pd.read_csv(file)
    diamonds = diamonds[(diamonds.x * diamonds.y * diamonds.z != 0) & (diamonds.price > 0)]
    for col in ['cut', 'color', 'clarity']:
            diamonds[col] = pd.Categorical(diamonds[col])

    return diamonds


model = joblib.load("./notebooks/models/XGBoost/03-07-2024-00-53-12/model.joblib")

data_file = "https://raw.githubusercontent.com/xtreamsrl/xtream-ai-assignment-engineer/main/datasets/diamonds/diamonds.csv"
data = load_data(data_file) 


class Diamond(BaseModel):
    carat: float
    cut: str
    color: str
    clarity: str
    depth: float = None
    table: float = None
    x: float = None
    y: float = None
    z: float = None

class SampleRequest(BaseModel):
    cut: str
    color: str
    clarity: str
    weight: float
    n_samples: int = 5


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)