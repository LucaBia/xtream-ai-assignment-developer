from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import pandas as pd

app = FastAPI(title="Xtream Diamond Price Prediction API")

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