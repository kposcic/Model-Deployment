import joblib
import pandas as pd

# Load saved pipeline
MODEL_PATH = "superkart_sales_model_pipeline.joblib"
model = joblib.load(MODEL_PATH)

print("Model loaded successfully")

# One example observation
input_data = pd.DataFrame([{
    "Product_Weight": 12.5,
    "Product_Sugar_Content": "Regular",
    "Product_Allocated_Area": 0.05,
    "Product_Type": "Snack Foods",
    "Product_MRP": 150.0,
    "Store_Id": "OUT001",
    "Store_Establishment_Year": 1987,
    "Store_Size": "High",
    "Store_Location_City_Type": "Tier 2",
    "Store_Type": "Supermarket Type1"
}])

prediction = model.predict(input_data)

print("Predicted sales:", prediction[0])