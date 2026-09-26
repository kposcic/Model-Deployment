import os
import streamlit as st
import requests

BACKEND_URL = os.getenv(
    "BACKEND_URL",          # in fromtend contaner we can run something like '-e BACKEND_URL=http://superkart-backend:7860' 
                            # to set the backend url to the backend container name and port. This is used in distributed deployment.
                            # If not set, it will default to the local backend url for local testing. 
    "http://127.0.0.1:7860"
)

# Reference year used when the model's Store_Age_Years feature was created.
# This must remain consistent with the feature engineering used during training.
MODEL_REFERENCE_YEAR = 2026   


# --------------------------------------------------
# Page Setup
# --------------------------------------------------

# this is a streamlit function to set the page title, icon and layout. Browser tab/window title, not the large heading title inside the page.
st.set_page_config(     
    page_title="SuperKart Sales Prediction",
    page_icon="🛒",
    layout="wide"
)

# set the main title and caption for the page. This is displayed inside the page, not in the browser tab/window.
st.title("SuperKart Sales Prediction")
st.caption(
    "Predict product sales for an individual product "
    "or upload a CSV file for batch prediction."
)


# --------------------------------------------------
# Tabs
# We have two tabs, one for single prediction and one for batch prediction. 

single_tab, batch_tab = st.tabs(
    ["Single Prediction", "Batch Prediction"]
)


# ==================================================
# SINGLE PREDICTION
# ==================================================

with single_tab:    # within the 'single tab' in a window, create this below 
                    # 'with' just cretaes a context within which the code below is executed.
                    # Without 'with', I would need to call each streamlit function with the tab object, like single_tab.subheader(), single_tab.form(), etc.

    st.subheader("Product and Store Information")

    with st.form("single_prediction_form"): # 'form' groups all inputs under one submit action and avoids rerunning
                                            # the app every time an individual input value changes.

        col1, col2 = st.columns(2)   # split 10 inputs into 2 columns for 

        # --------------------------
        # Product Information - here we are creating the input fields for the product information in the first column. 
        # Each input field  is limited to the expected range of values for that feature.  
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
                ["Perishables", "Non Perishables"]
            )

            product_allocated_area = st.number_input(
                "Product Allocated Area",
                min_value=0.0,
                max_value=1.0
            )

        # --------------------------
        # Store Information - similar for col 2
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

        # When clicked, the form values are submitted together.
        # During the resulting Streamlit rerun, `submitted` is True.
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

    if submitted:   # when the form is submited, rerun the app, capture the new state of the inputs. 

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
            # Send POST request in JSON format to the backend API for single prediction (endpoint that we created in backend).  
            response = requests.post(
                f"{BACKEND_URL}/v1/predict",
                json=payload
            )
            # retreive the results if the request was successful (status code 200). If not, display an error message with the status code and response text.
            if response.status_code == 200:

                prediction = response.json()["Predicted_Sales"]
                # 'metric' is a streamlit function that displays a single value with a label in a prominent way (as oposed to say 'write' widget). 
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
# BATCH PREDICTION = we do similar for batch service, all created in another tab and file upload and download button.
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