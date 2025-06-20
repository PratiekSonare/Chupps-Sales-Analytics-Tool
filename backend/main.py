
import requests
import os
import io
from fastapi import FastAPI, Request, Path, Body
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict, Optional, Union
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
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


@app.post("/item-shade/{item_name}-{shade_name}")
def item_wise(item_name: str = Path(...), shade_name: str = Path(...), req: ForecastRequestItem = Body(...),):
    try:
        if not req.data:
            return {"error": "No data provided."}

        # Load into DataFrame
        df = pd.DataFrame(req.data)

        required_cols = {'purDate', 'item', 'shade', 'sales'}
        if not required_cols.issubset(df.columns):
            return {"error": f"Missing required columns. Required: {required_cols}"}

        # Parse dates
        df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')

        # Filter by item and shade
        df_filtered = df[(df['item'] == item_name) &
                         (df['shade'] == shade_name)]

        if df_filtered.empty:
            return {"error": f"No sales data found for item '{item_name}' and shade '{shade_name}'."}

        # Aggregate
        daily_item_sales = df_filtered.groupby(
            'purDate')['sales'].sum().reset_index()
        item_df = daily_item_sales.rename(
            columns={'purDate': 'ds', 'sales': 'y'})

        return item_df[['ds', 'y']].to_dict(orient='records')

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


class ImgChatRequest(BaseModel):
    # Fields from ChatRequest

    message: Union[str, None] = None
    image_url: Union[str, None] = None

    # Fields from ForecastRequest
    data: list  # Your time series data
    # Add other forecast parameters as needed


class ImgChatItemShade(BaseModel):
    item_name: str = Path(...)
    shade_name: str = Path(...)
    req: ForecastRequestItem = Body(...)


# GOOGLE Gemma 3 - Graph Analysis
@app.post("/api/imgchat")
async def image_with_ai_forecast(request: ImgChatRequest):
    print('LLM endpoint called')

    df = pd.DataFrame(request.data)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['yhat'],
        mode="lines",
        name="Forecast",
        line=dict(color='blue'),
        showlegend=True
    ))

    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['yhat_upper'],
        mode="lines",
        name="Max. Sales",
        showlegend=True
    ))

    # Trend line (trace3)
    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['trend'],
        mode="lines",
        line=dict(width=2),
        name="Trend",
        showlegend=True
    ))

    # Layout matching your frontend
    fig.update_layout(
        title="Forecast",
        margin=dict(t=50, l=50, r=50, b=50),
        xaxis_title="Date",
        yaxis_title="Sales"
    )

    # Convert figure to base64
    img_buffer = io.BytesIO()
    fig.write_image(img_buffer, format="png")
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    api_key = os.getenv("OPENROUTER_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenRouter API key missing")

    user_message = """You are a skilled data analyst that is experienced in analyzing sales forecasted charts. 
                      Analyze this time series sales forecasting graph for an open footwear brand in India. 
                      Give detailed analysis based on the images of the three lines displayed in the image. 
                      Prophet model by Meta was used for forecasting of this sales data with yearly seasonality.
                      Give insights on the graph observations, avoid talking about the prophet model and the lines, rather talk about what the graph could mean for sales of footwear in India. 
                      Relate this sales to the geological, tropical and potential customers that we can reach out to in India, preferably metro cities.
                      The blue line is the forecasted sales, the red line is the maximum expected sales and the green line is the trend of sales. Be concise."""

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Sales Dashboard",
            },
            data=json.dumps({
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_message
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64, {img_base64}"
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


@app.post("/api/imgchat/itemshade/{item_name}")
async def image_with_ai_forecast(item_name: str = Path(...), req: dict = Body(...)):
    print('LLM endpoint called')

    df = pd.DataFrame(req['data'])  # assuming request payload key is 'data'
    df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')

    df = df[df['item'] == item_name]

    unique_shades = df['shade'].unique()
    num_shades = len(unique_shades)
    cols = 3
    rows = (num_shades + cols - 1) // cols  # ceiling division

    # Plotly subplots
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=unique_shades)

    for idx, shade in enumerate(unique_shades):
        row = (idx // cols) + 1
        col = (idx % cols) + 1

        df_filtered = df[df['shade'] == shade]
        daily_sales = df_filtered.groupby(
            'purDate')['sales'].sum().reset_index()

        fig.add_trace(
            go.Scatter(
                x=daily_sales['purDate'],
                y=daily_sales['sales'],
                name=shade,
                mode='lines'
            ),
            row=row,
            col=col
        )

    fig.update_layout(
        height=rows * 300,
        width=1200,
        title_text="Day-wise Sales per Shade (Open Footwear)",
        showlegend=False,
        margin=dict(t=80)
    )

    # Convert to base64 image
    img_buffer = io.BytesIO()
    fig.write_image(img_buffer, format="png")
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

    # LLM Prompt
    user_message = f"""
            You are a highly skilled product analyst for a footwear brand sold in India. The chart shows **daily sales trends** of multiple color shades of one item. Each subplot corresponds to a unique shade, visualized individually for clear trend recognition.

            Please analyze this sales data by addressing the following:

            1. Which shades appear most successful, and which ones underperform?
            2. What social, seasonal, or cultural patterns might explain demand spikes or drops?
            3. Which shade pairs show similar behavior and could be bundled or co-marketed?
            4. How can geography (e.g., metro cities, humid vs. dry zones) influence these sales?
            5. Based on the trends, what marketing or product strategies would you suggest for the Indian market?

            Avoid technical terms like “time series” or “subplots.” Instead, speak in a product-marketing and retail analysis tone for a footwear team.
            """

    api_key = os.getenv("OPENROUTER_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenRouter API key missing")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Sales Dashboard",
            },
            data=json.dumps({
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": user_message
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ],
            })
        )
        return response.json()

        console.log('image chat for itemshade: ', response.json())

    except requests.exceptions.RequestException as e:
        error_detail = f"OpenRouter request failed: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_detail += f" - Response: {e.response.text}"
        raise HTTPException(status_code=502, detail=error_detail)
