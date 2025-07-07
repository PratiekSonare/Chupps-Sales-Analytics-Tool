import requests
import json
from fastapi import FastAPI, Request, Path, Body
from tensorflow.keras.models import load_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/predict')
async def predict(req: Dict = Body(...)):
    df = pd.DataFrame(req["data"])

    df = df[['Payment Method', 'Lineitem sku', 'Lineitem price', 'Shipping Zip', 'Shipping City', 'Shipping Province']]

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
        'pmethod' :  'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//pmethod_label_mapping.json',
        'state'   : 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//state_label_mapping.json',
        'sku'     : 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//sku_cancel_ratios.json',
        'city'    : 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//city_cancel_ratios.json',
        'pincode' : 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//pincode_cancel_ratios.json',
        'price'   : 'https://fhhikeqiawxgesbporoj.supabase.co/storage/v1/object/public/ml-inference-assets//price_cancel_ratios.json'
    }

    def fetch_map(url, key_field, value_field):
        resp = requests.get(url)
        data = resp.json()
        return {item[key_field]: item[value_field] for item in data}
    
    pmethod_map = fetch_map(urls["pmethod"], "payment_method", "pmethod_label")
    state_map   = fetch_map(urls["state"], "state", "state_label")
    sku_map     = fetch_map(urls["sku"], "product_sku", "scr")
    city_map    = fetch_map(urls["city"], "city", "ccr")
    pincode_map = fetch_map(urls["pincode"], "pincode", "pcr")
    price_map   = fetch_map(urls["price"], "product_price", "scr")

    # --- Transform df using maps ---
    df['payment_method'] = df['Payment Method'].map(pmethod_map).fillna(-1)
    df['state'] = df['Shipping Province'].map(state_map).fillna(-1)
    df['scr'] = df['Lineitem sku'].map(sku_map).fillna(0.0)
    df['ccr'] = df['Shipping City'].map(city_map).fillna(0.0)
    df['pcr'] = df['Shipping Zip'].map(pincode_map).fillna(0.0)
    df['prcr'] = df['Lineitem price'].map(price_map).fillna(0.0)

    # Final numeric DataFrame
    features_df = df[['payment_method', 'scr', 'ccr', 'pcr', 'prcr', 'state']]

    # --- Model prediction ---
    model = load_model("model/risk_model.keras")
    proba = model.predict(features_df)[0][0]

    return {"risk_score": float(proba)}
