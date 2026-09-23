import io
import joblib
import pandas as pd

from flask import Flask, request, jsonify, send_file

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent   # this will return the absolute directory of the file being executed, regardless of where I launch it from 
MODEL_PATH = BASE_DIR / "superkart_sales_model_pipeline.joblib"   # this joins that direcotry with the model filename; the end result is that the model path is anchored to the location of the app.py file, not the current working directory 

# Initialize Flask app
superkart_api = Flask("SuperKart Sales Predictor")


# Load trained model
model = joblib.load(MODEL_PATH)


# Required input columns for both single and batch prediction
REQUIRED_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category"
]

# decorator for the root endpoint
# this registers the 'home' function with the endpoint "/", i.e. when someone accesses the root URL of the API, this function will be called
@superkart_api.get("/")
def home():
    return "SuperKart Sales Prediction API is running"

# decorator for the single prediction endpoint
# predict_sales is called when a POST request is made to the "/v1/predict" endpoint
@superkart_api.post("/v1/predict")
def predict_sales():
    """
    Single prediction endpoint.
    Expects JSON with the 10 required input fields.
    """

    product_data = request.get_json()

    if product_data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in product_data]
    if missing_cols:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing_cols
        }), 400

    # Build input row in the exact order expected by the model
    sample = {col: product_data[col] for col in REQUIRED_COLUMNS}
    # Create a dataframe from the dictionary to ensure the model receives the input in the correct format
    input_data = pd.DataFrame([sample])

    # model.predict() returns one prediction per input row.
    # Since input_data contains one row, the returned array contains
    # one value, so [0] extracts that prediction.
    prediction = model.predict(input_data)[0]

    # Create and return a Flask JSON Response containing the predicted sales value.
    # Flask provides the response status, headers, and body to the web/application
    # server, which serializes them into an HTTP response and sends it to the client.
    return jsonify({
        "Predicted_Sales": float(prediction)
    })

# This below is for a batch processing which is similar to above. The difference is that we are passing the cvs files between the front and back ends and not the structured json data.
# Still looking for a POST under the endpoint "/v1/predictbatch" and the function is called predict_sales_batch. The function expects a CSV file upload under the key: file and returns a CSV file with an added Predicted_Sales column.
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """
    Batch prediction endpoint.
    Expects a CSV file upload under the key: file
    Returns a CSV file with an added Predicted_Sales column.
    """

    if "file" not in request.files:
        return jsonify({"error": "No file part found in request"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    try:
        batch_data = pd.read_csv(file)
    except Exception as e:
        return jsonify({
            "error": "Could not read CSV file",
            "details": str(e)
        }), 400

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in batch_data.columns]
    if missing_cols:
        return jsonify({
            "error": "CSV is missing required columns",
            "missing_columns": missing_cols
        }), 400

    # Keep only the required columns in the correct order
    input_data = batch_data[REQUIRED_COLUMNS].copy()

    predictions = model.predict(input_data)

    results = batch_data.copy()
    results["Predicted_Sales"] = predictions

    # Convert results DataFrame to CSV in memory
    output = io.StringIO()
    results.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="batch_predictions.csv"
    )


if __name__ == "__main__":
    superkart_api.run(debug=True)