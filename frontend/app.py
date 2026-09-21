import os
import streamlit as st
import requests

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:7860"
)

MODEL_REFERENCE_YEAR = 2026


# --------------------------------------------------
# Page Setup
# --------------------------------------------------

st.set_page_config(
    page_title="SuperKart Sales Prediction",
    page_icon="🛒",
    layout="wide"
)

st.title("SuperKart Sales Prediction")
st.caption(
    "Predict product sales for an individual product "
    "or upload a CSV file for batch prediction."
)


# --------------------------------------------------
# Tabs
# --------------------------------------------------

single_tab, batch_tab = st.tabs(
    ["Single Prediction", "Batch Prediction"]
)


# ==================================================
# SINGLE PREDICTION
# ==================================================

with single_tab:

    st.subheader("Product and Store Information")

    with st.form("single_prediction_form"):

        col1, col2 = st.columns(2)

        # --------------------------
        # Product Information
        # --------------------------

        with col1:

            product_weight = st.number_input(
                "Product Weight",
                min_value=0.0,
                max_value=100.0
            )

            product_sugar_content = st.selectbox(
                "Product Sugar Content",
                ["Regular", "Low Sugar", "No Sugar"]
            )

            product_id_char = st.selectbox(
                "Product ID Character",
                ["FD", "DR", "NC"]
            )

            product_type_category = st.selectbox(
                "Product Type Category",
                ["Perishable", "Non Perishable"]
            )

            product_allocated_area = st.number_input(
                "Product Allocated Area",
                min_value=0.0,
                max_value=1.0
            )

        # --------------------------
        # Store Information
        # --------------------------

        with col2:

            store_size = st.selectbox(
                "Store Size",
                ["Small", "Medium", "High"]
            )

            store_location_city_type = st.selectbox(
                "Store Location City Type",
                ["Tier 1", "Tier 2", "Tier 3"]
            )

            store_type = st.selectbox(
                "Store Type",
                [
                    "Departmental Store",
                    "Food Mart",
                    "Supermarket Type1",
                    "Supermarket Type2"
                ]
            )

            product_mrp = st.number_input(
                "Product MRP",
                min_value=0.0,
                max_value=500.0
            )

            store_establishment_year = st.number_input(
                "Store Establishment Year",
                min_value=1900,
                max_value=MODEL_REFERENCE_YEAR,
                step=1
            )

        submitted = st.form_submit_button(
            "Predict Sales",
            use_container_width=True
        )

    # Feature engineering used by the model
    store_age_years = (
        MODEL_REFERENCE_YEAR - store_establishment_year
    )

    # --------------------------
    # Send Single Prediction
    # --------------------------

    if submitted:

        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_MRP": product_mrp,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_location_city_type,
            "Store_Type": store_type,
            "Product_Id_char": product_id_char,
            "Store_Age_Years": store_age_years,
            "Product_Type_Category": product_type_category
        }

        try:

            response = requests.post(
                f"{BACKEND_URL}/v1/predict",
                json=payload
            )

            if response.status_code == 200:

                prediction = response.json()["Predicted_Sales"]

                st.metric(
                    label="Predicted Sales",
                    value=f"${prediction:,.2f}"
                )

            else:

                st.error(
                    f"Backend returned error "
                    f"{response.status_code}: {response.text}"
                )

        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to the backend service."
            )


# ==================================================
# BATCH PREDICTION
# ==================================================

with batch_tab:

    st.subheader("Batch Prediction")

    st.write(
        "Upload a CSV file containing the required "
        "model input columns."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded_file is not None:

        if st.button(
            "Predict Batch Sales",
            use_container_width=True
        ):

            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "text/csv"
                )
            }

            try:

                response = requests.post(
                    f"{BACKEND_URL}/v1/predictbatch",
                    files=files
                )

                if response.status_code == 200:

                    st.success(
                        "Predictions generated successfully."
                    )

                    st.download_button(
                        label="Download Predictions",
                        data=response.content,
                        file_name="batch_predictions.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                else:

                    st.error(
                        f"Backend returned error "
                        f"{response.status_code}: {response.text}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the backend service."
                )