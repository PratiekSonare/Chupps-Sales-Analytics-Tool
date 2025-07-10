
import requests
import os
import io
from io import BytesIO
from fastapi import FastAPI, Request, Path, Body, UploadFile, File
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
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
from tensorflow.keras.models import load_model
import joblib
import numpy as np

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
    model: str
    messages: List[Message]


@app.post("/api/chat")
async def chat_with_ai(request: ChatRequest):
    print('LLM endpoint called')

    api_key = os.getenv("OPENROUTER_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, detail="OpenRouter API key missing")

    # Primary and fallback models
    primary_model = request.model or "deepseek/deepseek-chat-v3-0324:free"
    fallback_model = "deepseek/deepseek-r1-0528:free"

    request_data = {
        "model": primary_model,
        "messages": [msg.dict() for msg in request.messages]
    }

    try:
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

        response.raise_for_status()
        result = response.json()

        # Check for missing or empty 'choices'
        if not result.get("choices") or not result["choices"][0].get("message", {}).get("content"):
            print(
                "Primary model returned empty or invalid response. Using fallback model.")
            raise Exception("Empty primary response")

        print("Primary model successful!")
        return result

    except Exception as e:
        print(f"Primary LLM failed: {e}")

        # Try fallback model
        fallback_data = {
            "model": fallback_model,
            "messages": [msg.dict() for msg in request.messages]
        }

        try:
            fallback_response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "Sales Dashboard (Fallback)",
                },
                json=fallback_data,
                timeout=30
            )

            fallback_response.raise_for_status()
            fallback_result = fallback_response.json()

            if not fallback_result.get("choices") or not fallback_result["choices"][0].get("message", {}).get("content"):
                raise Exception("Fallback also returned empty response")

            print("Fallback model successful!")
            return fallback_result

        except Exception as fallback_error:
            print(f"Fallback LLM failed: {fallback_error}")
            raise HTTPException(
                status_code=502, detail="Both primary and fallback LLMs failed.")


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

    user_message = """
    You are a skilled sales analyst specializing in time series sales forecasting and market insights.

    Analyze this time series sales forecast chart for an open footwear brand in India. The chart was generated using the Prophet model with yearly seasonality, but do not mention the model or the lines themselves.

    Instead, provide a clear, concise business-oriented analysis of what the forecast suggests about future sales patterns. Focus on interpreting the implications of the chart for the Indian footwear market, especially in relation to:

    - Geographic trends across India (e.g., metro cities vs. others)
    - Seasonal or climatic influences on demand (e.g., tropical regions)
    - Emerging opportunities in customer outreach or regional expansion
    - Any potential risk or downturns implied by the trends

    The three lines shown in the graph represent:
    - Blue: Forecasted sales
    - Red: Upper bound of expected sales
    - Green: Underlying sales trend
    
    Here is relevant metadata to inform your analysis: {request.message}

    Base your insights solely on the patterns and relationships in the graph, not on the technical components. Your goal is to help business stakeholders understand where and how to act to increase sales in India.
    """

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


@app.post("/api/itemshade/plotallshades/{item_name}")
async def get_plot_data(item_name: str, req: Dict = Body(...)):
    df = pd.DataFrame(req["data"])
    df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')
    df = df[df['item'] == item_name]

    result = {}

    for shade in df['shade'].unique():
        df_shade = df[df['shade'] == shade]
        daily_sales = df_shade.groupby('purDate')['sales'].sum().reset_index()

        result[shade] = {
            "x": daily_sales['purDate'].dt.strftime('%Y-%m-%d').tolist(),
            "y": daily_sales['sales'].tolist()
        }

    return {"traces": result}

# APRIORI ALGORITHM


@app.post("/api/bestshade")
async def bestShade(req: Dict = Body(...)):

    df = pd.DataFrame(req["data"])
    df['purDate'] = pd.to_datetime(df['purDate'], format='%Y-%m-%d')

    daily_sales = df.groupby(['purDate', 'shade'])['sales'].sum().reset_index()

    daily_sales['sold'] = daily_sales['sales'] >= 1
    transaction_df = daily_sales[daily_sales['sold']].pivot_table(
        index='purDate',
        columns='shade',
        values='sold',
        fill_value=0
    )

    frequent_itemsets = apriori(
        transaction_df, min_support=0.3, use_colnames=True)
    support_desc = frequent_itemsets.sort_values(by='support', ascending=False)
    greater_support = support_desc[support_desc['support'] > 0.5]

    greater_support['len'] = greater_support['itemsets'].apply(
        lambda x: len(x))
    pair_great_sup = greater_support[(greater_support['len'] == 2)].copy()

    # Convert itemsets into two separate columns
    pair_great_sup[['shade1', 'shade2']] = pair_great_sup['itemsets'].apply(
        lambda x: pd.Series(list(x))
    )

    # Return only the columns needed
    return pair_great_sup[['shade1', 'shade2', 'support']].to_dict(orient='records')


@app.post('/predict')
async def predict(req: Dict = Body(...)):
    df = pd.DataFrame(req["data"])

    df = df[['Payment Method', 'Lineitem sku', 'Lineitem price',
             'Shipping Zip', 'Shipping City', 'Shipping Province']]

    # --- Data cleaning ---
    df['Payment Method'] = df['Payment Method'].fillna('Other')
    df['Payment Method'] = df['Payment Method'].replace({
        'Cash on Delivery (COD)': 'COD',
        'Other': 'PREPAID',
        '1Razorpay - UPI, Cards, Wallets, NB': 'PREPAID',
        '1Cashfree Payments(UPI,Cards,Net Banking,Wallets)': 'PREPAID',
        'manual': 'PREPAID',
        '1Razorpay - UPI, Cards, Wallets, NB + Cash on Delivery (COD)': 'PREPAID'
    })
    df['Shipping Zip'] = df['Shipping Zip'].astype(str).str.lstrip("'")
    df['Lineitem price'] = df['Lineitem price'].replace({
        649.0: 699.0, 849.0: 899.0, 949.0: 999.0, 1049.0: 1099.0, 749.0: 799.0
    })
    df['Shipping City'] = df['Shipping City'].str.lower()

    # --- Load label and ratio maps from Supabase ---
    urls = {
        'pmethod':  'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//pmethod_label_mapping.json',
        'state': 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//state_label_mapping.json',
        'sku': 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//sku_cancel_ratios.json',
        'city': 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//city_cancel_ratios.json',
        'pincode': 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//pincode_cancel_ratios.json',
        'price': 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//price_cancel_ratios.json'
    }

    def fetch_map(url, key_field=None, value_field=None):
        resp = requests.get(url)
        data = resp.json()
        # print(data)
        return data

    def fetch_map_dict(url, key_field, value_field):
        resp = requests.get(url)
        data = resp.json()
        # print(data)
        return {item[key_field]: item[value_field] for item in data}

    pmethod_map = fetch_map(urls["pmethod"])
    state_map = fetch_map(urls["state"])
    sku_map = fetch_map_dict(urls["sku"], "product_sku", "scr")
    city_map = fetch_map_dict(urls["city"], "city", "ccr")
    pincode_map = fetch_map_dict(urls["pincode"], "pincode", "pcr")
    price_map = fetch_map_dict(urls["price"], "product_price", "prcr")

    # --- Transform df using maps ---
    mean_pcr = np.mean(list(pincode_map.values()))
    mean_scr = np.mean(list(sku_map.values()))
    mean_ccr = np.mean(list(city_map.values()))
    mean_prcr = np.mean(list(price_map.values()))

    # df['payment_method'] = df['Payment Method'].map(pmethod_map).fillna(-1)
    # df['state'] = df['Shipping Province'].map(state_map).fillna(-1)
    # df['scr'] = df['Lineitem sku'].map(sku_map).fillna(mean_scr)
    # df['ccr'] = df['Shipping City'].map(city_map).fillna(mean_ccr)
    # df['pcr'] = df['Shipping Zip'].map(pincode_map).fillna(mean_pcr)
    # df['prcr'] = df['Lineitem price'].map(price_map).fillna(mean_prcr)

    df['payment_method'] = df['Payment Method'].map(pmethod_map).fillna(-1)
    df['state'] = df['Shipping Province'].map(state_map).fillna(-1)
    df['scr'] = df['Lineitem sku'].map(sku_map).fillna(0.0)
    df['ccr'] = df['Shipping City'].map(city_map).fillna(0.0)
    df['pcr'] = df['Shipping Zip'].map(pincode_map).fillna(0.0)
    df['prcr'] = df['Lineitem price'].map(price_map).fillna(0.0)

    # Final numeric DataFrame
    scaler = joblib.load("model/scaler.joblib")
    features_df = df[['payment_method', 'scr', 'ccr', 'pcr', 'prcr', 'state']]
    features_scaled = scaler.transform(features_df)

    # --- Model prediction ---
    model = load_model("model/risk_model_nn.keras")
    proba = model.predict(features_scaled)[0][0]

    return {"risk_score": float(proba)}


@app.post('/input/clean/full')
async def clean(file: UploadFile = File(...)):

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents), header=2)

    df = df[['BILL DATE', 'PARTY NAME', 'SHADE NAME', 'SUB CATEGORY',
             'GENDER', 'ADDITIONAL ITEM NAME', 'NET QTY', 'M.R.P.', 'PACK / SIZE']]
    df.rename(columns={'BILL DATE': 'purDate', 'PARTY NAME': 'party', 'SHADE NAME': 'shade', 'SUB CATEGORY': 'item',
              'GENDER': 'gender', 'ADDITIONAL ITEM NAME': 'sku', 'NET QTY': 'sales', 'M.R.P.': 'mrp', 'PACK / SIZE': 'size'}, inplace=True)
    df['gender'] = df['gender'].replace(
        {'MEN': 'MENS', 'Mens': 'MENS', 'Women': 'WOMENS', 'Womens': 'WOMENS', 'WOMEN': 'WOMENS', 'Unisex': 'UNISEX'})
    df.dropna(inplace=True)
    df['purDate'] = pd.to_datetime(df['purDate'], format='%d/%m/%Y')

    discard_items = ['750X550X335 5PLY CARTON', '320X130X120MM INNER BOX',
                     '100X60MM TAG', 'FOOTWEAR SOLE EVA', 'ASSORTED']
    rows_to_keep = ~df['item'].isin(discard_items)
    df = df[rows_to_keep].copy()

    df[['sales', 'mrp', 'size']] = df[['sales', 'mrp', 'size']].astype('int64', errors='ignore')
    
    df['party'] = df['party'].replace({
        'ADITI FOOTWEAR                -CHITTORGARH': 'ADITI FOOTWEAR',
        'AG TRENDS                     -HYDRABAD': 'AG TRENDS',
        'AIREN ENTERPRISES             -HISAR': 'AIREN ENTERPRISES',
        'BAGGA SALES AGENCY            -AHEDABAD': 'BAGGA SALES AGENCY',
        'DEVRAJ AND SONS               -KORAPUT': 'DEVRAJ AND SONS',
        'GNM FOOTWEAR                  -DELHI': 'GNM FOOTWEAR',
        'GURU SHOES TECH PVT. LTD      -AGRA': 'GURU SHOES TECH PVT. LTD',
        'J.S.DISTRIBUTOR               -BANGLORE': 'J.S.DISTRIBUTORS',
        'JAYSHREE MARKETING            -BHOPAL': 'JAYSHREE MARKETING',
        'KIRANAKART TECHNOLOGIES PVT LTD -MUMBAI': 'KIRANAKART TECHNOLOGIES PVT LTD',
        'KIRANAKART TECHNOLOGIES PVT LTD BR -BANGLORE': 'KIRANAKART TECHNOLOGIES PVT LTD',
        'KIRANAKART TECHNOLOGIES PVT LTD CH -CHENNAI': 'KIRANAKART TECHNOLOGIES PVT LTD',
        'KIRANAKART TECHNOLOGIES PVT LTD HR -GURUGRAM': 'KIRANAKART TECHNOLOGIES PVT LTD',
        'KWALITY ENTERPRISES           -BHAWANIPATNA': 'KWALITY ENTERPRISES',
        'M/S SHOE PARK                 -JAGDALPUR': 'M/S SHOEPARK (JAGDALPUR)',
        'M/S STYLE SHOES               -BHUBNESHWAR': 'M/S STYLE SHOES',
        'MAHARAJA ENTERPRISES          -RAIPUR': 'MAHARAJA ENTERPRISES',
        'MANOHAR BOOT HOUSE            -BILASPUR': 'MANOHAR BOOT HOUSE',
        'MK FOOTWEAR                   -HARIDWAR': 'MK FOOTWEAR',
        'NEW STAR FOOTWEAR             -KORAPUT': 'NEW STAR FOOTWEAR ODISHA',
        'RAMDEV SHOE TRADING COMPANY   -CHENNAI': 'RAMDEV SHOE TRADING COMPANY',
        'BOOTS MADGAON                 -GOA': 'BOOTS',
        'BOOTS PANJI                   -GOA': 'BOOTS',
        'CENTRO (V-RETAIL PVT LTD - WAREHOUSE)': 'CENTRO',
        'CENTRO - CNR-CEN (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO SAGX (V-RETAIL LTD)    -HYDRABAD': 'CENTRO',
        'CENTRO SAGX (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- 6 MALL SS (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- ASRN (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- CP (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- FRM (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- GBS (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- HNR (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- KMPL (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- KP (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- KPT-LB (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- KRK (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO- VZM (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-CELEST (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-GSM-SS (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-HNK-CEN (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-KKD-SBR-CEN (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-KKD-SRMT (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-KRM-CEN (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-LNT-L4-SS (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-MALHAR (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-NIZAMABAD (V-RETAIL PVT LTD)': 'CENTRO',
        'CENTRO-SCM-SS (V-RETAIL PVT LTD)': 'CENTRO',
        'SIKKIM COMMERCIAL             -BHUBNESHWAR': 'SIKKIM COMMERCIAL',
        'SIKKIM COMMERCIAL CORPORATION -KOLKATA': 'SIKKIM COMMERCIAL CORPORATION',
        'SHREE KRISHNA FOOTWEAR        -BAHADURGARH': 'SHREE KRISHNA FOOTWEAR',
        'SHREEJI FOOTWEAR              -BAHADURGARH': 'SHREEJI FOOTWEAR',
        'MAA VAISHNAVI INTERNATIONAL   -GURUGRAM': 'MAA VAISHNAVI INTERNATIONAL',
        'STEP IN                       -RANCHI': 'STEP IN',
        'SURE LEATHER EXPORTS          -AGRA': 'SURE LEATHER EXPORTS',
        'TATA UNISTORE LIMITED-KORALURU -BANGALORE': 'TATA UNISTORE LIMITED',
        'TWAM ENTERPRISE               -THANE': 'TWAM ENTERPRISE',
        'M/S SOFT WALK                 -BHADRAK': 'M/S SOFT WALK'
    })

    distributor_location_map = {
        'ADITI FOOTWEAR': 'CHITTORGARH',
        'AG TRENDS': 'HYDERABAD',
        'AIREN ENTERPRISES': 'HISAR',
        'BAGGA SALES AGENCY': 'AHMEDABAD',
        'DEVRAJ AND SONS': 'KORAPUT',
        'GNM FOOTWEAR': 'DELHI',
        'GURU SHOES TECH PVT. LTD': 'AGRA',
        'J.S.DISTRIBUTORS': 'BANGALORE',
        'JAYSHREE MARKETING': 'BHOPAL',
        'KIRANAKART TECHNOLOGIES PVT LTD': 'MULTIPLE',
        'KWALITY ENTERPRISES': 'BHAWANIPATNA',
        'M/S SHOEPARK (JAGDALPUR)': 'JAGDALPUR',
        'M/S STYLE SHOES': 'BHUBANESWAR',
        'MAHARAJA ENTERPRISES': 'RAIPUR',
        'MANOHAR BOOT HOUSE': 'BILASPUR',
        'MK FOOTWEAR': 'HARIDWAR',
        'NEW STAR FOOTWEAR ODISHA': 'KORAPUT',
        'RAMDEV SHOE TRADING COMPANY': 'CHENNAI',
        'SIKKIM COMMERCIAL': 'BHUBANESWAR',
        'SIKKIM COMMERCIAL CORPORATION': 'KOLKATA',
        'SHREE KRISHNA FOOTWEAR': 'BAHADURGARH',
        'SHREEJI FOOTWEAR': 'BAHADURGARH',
        'MAA VAISHNAVI INTERNATIONAL': 'GURUGRAM',
        'STEP IN': 'RANCHI',
        'SURE LEATHER EXPORTS': 'AGRA',
        'TATA UNISTORE LIMITED': 'BANGALORE',
        'TWAM ENTERPRISE': 'THANE',
        'CENTRO': 'MULTIPLE'
    }

    location_zone_map = {
        'AGRA': 'NORTH',
        'AHMEDABAD': 'WEST',
        'BAHADURGARH': 'EAST',
        'BANGALORE': 'SOUTH',
        'BHAWANIPATNA': 'EAST',
        'BHOPAL': 'WEST',
        'BHUBANESWAR': 'EAST',
        'BILASPUR': 'NORTH',
        'CHENNAI': 'SOUTH',
        'CHITTORGARH': 'WEST',
        'DELHI': 'NORTH',
        'GURUGRAM': 'NORTH',
        'HARIDWAR': 'NORTH',
        'HISAR': 'NORTH',
        'HYDERABAD': 'SOUTH',
        'JAGDALPUR': 'NORTH',
        'KOLKATA': 'EAST',
        'KORAPUT': 'EAST',
        'RAIPUR': 'NORTH',
        'RANCHI': 'EAST',
        'THANE': 'WEST',
    }

    location_to_state = {
        'AGRA': 'Uttar Pradesh',
        'AHMEDABAD': 'Gujarat',
        'BAHADURGARH': 'Haryana',
        'BANGALORE': 'Karnataka',
        'BHAWANIPATNA': 'Odisha',
        'BHOPAL': 'Madhya Pradesh',
        'BHUBANESWAR': 'Odisha',
        'BILASPUR': 'Chhattisgarh',
        'CHENNAI': 'Tamil Nadu',
        'CHITTORGARH': 'Rajasthan',
        'DELHI': 'Delhi',
        'GURUGRAM': 'Haryana',
        'HARIDWAR': 'Uttarakhand',
        'HISAR': 'Haryana',
        'HYDERABAD': 'Telangana',
        'JAGDALPUR': 'Chhattisgarh',
        'KOLKATA': 'West Bengal',
        'KORAPUT': 'Odisha',
        'MULTIPLE': 'UNKNOWN',
        'RAIPUR': 'Chhattisgarh',
        'RANCHI': 'Jharkhand',
        'THANE': 'Maharashtra',
        'UNKNOWN': 'UNKNOWN'
    }

    df['location'] = df['party'].map(distributor_location_map)
    df['location'] = df['location'].fillna('UNKNOWN')

    df['state'] = df['location'].map(location_to_state)

    df['zone'] = df['location'].map(location_zone_map)
    df['zone'] = df['zone'].fillna('UNKNOWN')

    print("cleaning successful!")
    print("full data: ", df.shape)

    return df.to_dict(orient="records")


@app.post('/input/clean/agg')
async def clean(file: UploadFile = File(...)):

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents), header=2)

    df = df[['BILL DATE', 'NET QTY', 'SUB CATEGORY']]
    df.rename(columns={'BILL DATE': 'ds', 'NET QTY': 'y', 'SUB CATEGORY': 'item'}, inplace=True)
    df.dropna(inplace=True)
    discard_items = ['750X550X335 5PLY CARTON', '320X130X120MM INNER BOX',
                     '100X60MM TAG', 'FOOTWEAR SOLE EVA', 'ASSORTED']
    rows_to_keep = ~df['item'].isin(discard_items)
    df = df[rows_to_keep].copy()

    df = df[['ds', 'y']]
    df['ds'] = pd.to_datetime(df['ds'], format='%d/%m/%Y')
    df['y'] = df['y'].astype('int64', errors='ignore')

    # Aggregate df day-wise, y = sum
    df = df.groupby('ds')['y'].sum().reset_index()

    print("agg data: ", df.head(2))

    return df.to_dict(orient="records")
