import joblib
import pandas as pd

MODEL_PATH = "superkart_sales_model_pipeline.joblib"
BATCH_PATH = "Batch_Data_SuperKart.csv"

# Load model
model = joblib.load(MODEL_PATH)

print("Model loaded successfully")

# Load the actual batch input file
batch_data = pd.read_csv(BATCH_PATH)

print("\nBatch input columns:")
print(batch_data.columns.tolist())

# Run predictions on every row
predictions = model.predict(batch_data)

print("\nPredictions:")
print(predictions)

# Add predictions to a copy so we can inspect results
results = batch_data.copy()
results["Predicted_Sales"] = predictions

print("\nResults:")
print(results)

single_input = batch_data.iloc[[0]]

single_prediction = model.predict(single_input)

print("\nSingle prediction:")
print(single_prediction[0])