from fastapi import FastAPI, Request
from pydantic import BaseModel
import pandas as pd
from prophet import Prophet
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for Svelte frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with your frontend URL in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ForecastRequest(BaseModel):
    data: list  # List of { ds: date, y: value }


@app.post("/forecast")
def forecast(req: ForecastRequest):

    # load df
    df = pd.DataFrame(req.data)
    df['ds'] = pd.to_datetime(df['ds'], format="%Y-%m-%d")

    # define model
    years = range(df['ds'].dt.year.min(), df['ds'].dt.year.max() + 3)
    
    feb_mar_spike = pd.DataFrame({
        'holiday': 'feb_mar_spike',
        'ds': pd.to_datetime([f'{year}-03-01' for year in years]),
        'lower_window': -4,
        'upper_window': 10
    })

    # Initialize and fit the model with holidays
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        holidays=feb_mar_spike,
        holidays_prior_scale=10
    )
    model.fit(df)

    # make predictions
    future = model.make_future_dataframe(periods=365)
    forecast = model.predict(future)

    result = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 'trend']].to_dict(orient='records')
    return result
