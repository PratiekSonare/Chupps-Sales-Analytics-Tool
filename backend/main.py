
import requests
import os
from fastapi import FastAPI, Request, Path
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict, Optional
from prophet import Prophet
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import json

load_dotenv(".env.local")


app = FastAPI()

# # Enable CORS for Svelte frontend
app.add_middleware(
    CORSMiddleware,
    # Replace * with your frontend URL in prod
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ForecastRequest(BaseModel):
    data: list  # List of { ds: date, y: value }


@app.post("/forecast")
def forecast(req: ForecastRequest):

    # load df - aggregated data
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

    result = forecast[['ds', 'yhat', 'yhat_lower',
                       'yhat_upper', 'trend']].to_dict(orient='records')
    return result


# original data, product filters
class ForecastRequestItem(BaseModel):
    data: List[Dict]  # List of { ds: date, y: value }


@app.post("/forecast/item/{item_name}")
def forecast_item_wise(item_name: str = Path(...), req: ForecastRequestItem = None):
    try:
        print("Running forecast for item: ", {item_name})

        if req is None or not req.data:
            return {"error": "No data provided."}

        # Load data into DataFrame
        df = pd.DataFrame(req.data)

        # print('original df: ', df)

        # Check required columns
        required_cols = {'purDate', 'item', 'sales'}
        if not required_cols.issubset(df.columns):
            return {"error": f"Missing required columns. Required: {required_cols}"}

        # Parse and filter
        df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')
        df = df[df['item'] == item_name]

        if df.empty:
            return {"error": f"No sales data found for item '{item_name}'."}

        # Aggregate
        daily_item_sales = df.groupby('purDate')['sales'].sum().reset_index()
        item_df = daily_item_sales.rename(
            columns={'purDate': 'ds', 'sales': 'y'})

        # Prophet forecasting
        model = Prophet(yearly_seasonality=True,
                        weekly_seasonality=False, daily_seasonality=False)
        model.fit(item_df)

        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)

        result = forecast[['ds', 'yhat', 'yhat_lower',
                           'yhat_upper', 'trend']].to_dict(orient='records')
        return result

    except Exception as e:
        return {"error": str(e)}


@app.post("/item/{item_name}")
def item_wise(item_name: str = Path(...), req: ForecastRequestItem = None):
    try:

        if req is None or not req.data:
            return {"error": "No data provided."}

        # Load data into DataFrame
        df = pd.DataFrame(req.data)

        # print('original df: ', df)

        # Check required columns
        required_cols = {'purDate', 'item', 'sales'}
        if not required_cols.issubset(df.columns):
            return {"error": f"Missing required columns. Required: {required_cols}"}

        # Parse and filter
        df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')
        df = df[df['item'] == item_name]

        if df.empty:
            return {"error": f"No sales data found for item '{item_name}'."}

        # Aggregate
        daily_item_sales = df.groupby('purDate')['sales'].sum().reset_index()
        item_df = daily_item_sales.rename(
            columns={'purDate': 'ds', 'sales': 'y'})

        result = item_df[['ds', 'y']].to_dict(orient='records')
        return result

    except Exception as e:
        return {"error": str(e)}


@app.post("/shade/{shade_name}")
def shade_wise(shade_name: str = Path(...), req: ForecastRequestItem = None):
    try:

        if req is None or not req.data:
            return {"error": "No data provided."}

        # Load data into DataFrame
        df = pd.DataFrame(req.data)

        # Check required columns
        required_cols = {'purDate', 'shade', 'sales'}
        if not required_cols.issubset(df.columns):
            return {"error": f"Missing required columns. Required: {required_cols}"}

        # Parse and filter
        df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')
        df = df[df['shade'] == shade_name]

        if df.empty:
            return {"error": f"No sales data found for item '{shade_name}'."}

        # Aggregate
        daily_shade_sales = df.groupby('purDate')['sales'].sum().reset_index()
        shade_df = daily_shade_sales.rename(
            columns={'purDate': 'ds', 'sales': 'y'})

        result = shade_df[['ds', 'y']].to_dict(orient='records')
        return result

    except Exception as e:
        return {"error": str(e)}


@app.post("/forecast/shade/{shade_name}")
def forecast_shade_wise(shade_name: str = Path(...), req: ForecastRequestItem = None):
    try:
        if req is None or not req.data:
            return {"error": "No data provided."}

        print('shade forecast running..')

        # Load data into DataFrame
        df = pd.DataFrame(req.data)

        # Check required columns
        required_cols = {'purDate', 'shade', 'sales'}
        if not required_cols.issubset(df.columns):
            return {"error": f"Missing required columns. Required: {required_cols}"}

        # Parse and filter
        df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')
        df = df[df['shade'] == shade_name]

        if df.empty:
            return {"error": f"No sales data found for item '{shade_name}'."}

        # Aggregate
        daily_shade_sales = df.groupby('purDate')['sales'].sum().reset_index()
        shade_df = daily_shade_sales.rename(
            columns={'purDate': 'ds', 'sales': 'y'})

        # Prophet forecasting
        model = Prophet(yearly_seasonality=True,
                        weekly_seasonality=False, daily_seasonality=False)
        model.fit(shade_df)

        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)

        result = forecast[['ds', 'yhat', 'yhat_lower',
                           'yhat_upper', 'trend']].to_dict(orient='records')
        return result

    except Exception as e:
        return {"error": str(e)}

# DEEPSEEK response - DeepSeek: DeepSeek V3 0324


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "deepseek/deepseek-r1-0528:free"


@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    print('LLM endpoint called')

    api_key = os.getenv("OPENROUTER_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenRouter API key missing")

    try:
        # Debug print the request we're sending
        request_data = {
            "model": request.model or "openai/gpt-3.5-turbo",
            "messages": [msg.dict() for msg in request.messages]
        }

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Sales Dashboard",
            },
            json=request_data,
            timeout=30
        )

        # Print raw response for debugging
        # print(f"OpenRouter response: {response.status_code} - {response.text}")
        print("llm called successfully!")

        response.raise_for_status()
        print('backend llm response: ', response)
        return response.json()

    except requests.exceptions.RequestException as e:
        error_detail = f"OpenRouter request failed: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_detail += f" - Response: {e.response.text}"
        print(error_detail)
        raise HTTPException(status_code=502, detail=error_detail)

# GOOGLE Gemma 3 - Graph Analysis
@app.post("/api/imgchat")
async def chat_with_ai(request: ChatRequest):
    print('LLM endpoint called')

    api_key = os.getenv("OPENROUTER_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenRouter API key missing")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What is in this image?"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
                                }
                            }
                        ]
                    }
                ],
            })
        )
        return response.json()

    except requests.exceptions.RequestException as e:
        error_detail = f"OpenRouter request failed: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_detail += f" - Response: {e.response.text}"
        print(error_detail)
        raise HTTPException(status_code=502, detail=error_detail)
