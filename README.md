# SuperKart Sales Prediction - Model Deployment

## Project Overview

This project deploys a machine learning model developed for **SuperKart**, a retail chain operating supermarkets and food marts across different store types and city tiers.

The model predicts **product-store sales revenue** from product and store characteristics.

The deployment consists of two independently containerized applications:

- **Backend:** Flask REST API served by Gunicorn
- **Frontend:** Streamlit web application

The trained machine learning pipeline is serialized using `joblib` and loaded by the backend API.

The application supports:

- Single product/store sales prediction
- Batch prediction using a CSV file
- Browser-based interaction through Streamlit
- REST API access directly to the Flask backend

The deployment was developed and tested locally, reproduced in a **GitHub Codespace**, and the final Docker images were published to **GitHub Container Registry (GHCR)**.

---

## Application Architecture

```text
User Browser
     |
     | HTTP / HTTPS
     v
Streamlit Frontend
Port 8501
     |
     | HTTP REST request
     v
Flask / Gunicorn Backend
Port 7860
     |
     v
Serialized ML Pipeline
     |
     v
Predicted Sales
```

The frontend is responsible for collecting user input and displaying results.

The backend is responsible for:

1. Receiving prediction requests
2. Converting the input into the format expected by the model
3. Calling the trained machine learning pipeline
4. Returning the predicted sales value

---

## Repository Structure

```text
Model-Deployment/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── superkart_sales_model_pipeline.joblib
│
├── frontend/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── test/
│   └── app-test.py
│
├── test-data/
│   └── Batch_Data_SuperKart.csv
│
├── .gitignore
└── README.md
```

---

## Model Inputs

The deployed model expects the following 10 input features:

1. `Product_Weight`
2. `Product_Sugar_Content`
3. `Product_Allocated_Area`
4. `Product_MRP`
5. `Store_Size`
6. `Store_Location_City_Type`
7. `Store_Type`
8. `Product_Id_char`
9. `Store_Age_Years`
10. `Product_Type_Category`

The predicted output is:

```text
Predicted_Sales
```

`Store_Age_Years` is derived from the store establishment year using the same reference year used during model training.

---

# Backend

## Backend Technology

The backend uses:

- Python
- Flask
- Gunicorn
- pandas
- NumPy
- scikit-learn
- joblib

Flask defines the REST API endpoints and handles the request and response data.

Gunicorn acts as the production WSGI server that runs the Flask application.

The trained model pipeline is loaded from:

```text
superkart_sales_model_pipeline.joblib
```

---

## Backend API Endpoints

### API Status

```text
GET /
```

Used to confirm that the API is running.

Example response:

```text
SuperKart Sales Prediction API is running
```

---

### Single Prediction

```text
POST /v1/predict
```

The endpoint accepts a JSON object containing one product/store observation.

Example request:

```json
{
    "Product_Weight": 12.5,
    "Product_Sugar_Content": "Regular",
    "Product_Allocated_Area": 0.05,
    "Product_MRP": 150.0,
    "Store_Size": "Medium",
    "Store_Location_City_Type": "Tier 2",
    "Store_Type": "Supermarket Type1",
    "Product_Id_char": "FD",
    "Store_Age_Years": 10,
    "Product_Type_Category": "Perishable"
}
```

Example response:

```json
{
    "Predicted_Sales": 4025.6263406750063
}
```

---

### Batch Prediction

```text
POST /v1/predictbatch
```

The endpoint accepts a CSV file using:

```text
multipart/form-data
```

The backend reads the uploaded CSV, generates a prediction for each row, and returns a new CSV file containing the original data plus:

```text
Predicted_Sales
```

Unlike the single-prediction endpoint, the batch endpoint returns a **CSV file rather than JSON**.

---

# Frontend

## Frontend Technology

The frontend uses:

- Python
- Streamlit
- Requests

Streamlit provides the browser-based user interface.

The Python `requests` library is used by the frontend to send HTTP requests to the Flask backend.

The frontend supports two modes:

- Single Prediction
- Batch Prediction

---

## Frontend-to-Backend Communication

The frontend retrieves the backend address using an environment variable:

```python
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:7860"
)
```

If the environment variable `BACKEND_URL` is supplied when the container starts, that value is used.

Otherwise, the application falls back to:

```text
http://127.0.0.1:7860
```

This allows the same frontend image to be used in different deployment environments without changing the application code.

---

# Docker Deployment

## Backend Docker Image

The backend image can be built with:

```bash
docker build -t superkart-backend:latest ./backend
```

The backend Dockerfile runs Gunicorn on:

```text
0.0.0.0:7860
```

This allows the application to accept connections arriving at container port `7860`.

---

## Frontend Docker Image

The frontend image can be built with:

```bash
docker build -t superkart-frontend:latest ./frontend
```

Streamlit listens inside the container on:

```text
0.0.0.0:8501
```

---

# Running Locally with Docker

For a normal local Docker deployment, the frontend and backend can communicate directly through a user-defined Docker network.

Create the Docker network:

```bash
docker network create superkart-network
```

Start the backend:

```bash
docker run -d \
  --name superkart-backend \
  --network superkart-network \
  -p 7860:7860 \
  superkart-backend:latest
```

Start the frontend:

```bash
docker run -d \
  --name superkart-frontend \
  --network superkart-network \
  -p 8501:8501 \
  -e BACKEND_URL=http://superkart-backend:7860 \
  superkart-frontend:latest
```

The frontend can then reach the backend using the Docker DNS name:

```text
http://superkart-backend:7860
```

The browser can access the Streamlit frontend through:

```text
http://localhost:8501
```

---

## Docker Port Publishing

The backend uses:

```text
-p 7860:7860
```

which means:

```text
Docker host port 7860
        ↓
Backend container port 7860
```

The frontend uses:

```text
-p 8501:8501
```

which means:

```text
Docker host port 8501
        ↓
Frontend container port 8501
```

Docker installs the required forwarding/NAT rules in the host networking stack.

For example:

```text
0.0.0.0:8501->8501/tcp
```

means that TCP traffic arriving on port `8501` on any IPv4 interface of the Docker host can be forwarded to port `8501` of the frontend container.

It does not broadcast the traffic to all containers.

---

# GitHub Codespaces Deployment

The project was pushed to GitHub and then rebuilt inside a GitHub Codespace to verify that the deployment could be reproduced from the repository.

The backend and frontend Docker images were built from the Dockerfiles stored in the repository.

---

## Codespaces Backend Container

The backend container was started using:

```bash
docker run -d \
  --name superkart-backend \
  -p 7860:7860 \
  superkart-backend:latest
```

This publishes backend container port `7860` on Docker host port `7860`.

---

## Codespaces Frontend Container

In the Codespaces environment, direct container-to-container TCP communication through a custom Docker bridge network did not work correctly even though Docker DNS resolution succeeded.

A Codespaces-specific workaround was therefore used.

The frontend container was started with:

```bash
docker run -d \
  --name superkart-frontend \
  -p 8501:8501 \
  --add-host=host.docker.internal:host-gateway \
  -e BACKEND_URL=http://host.docker.internal:7860 \
  superkart-frontend:latest
```

The two important options are:

```text
--add-host=host.docker.internal:host-gateway
```

and:

```text
-e BACKEND_URL=http://host.docker.internal:7860
```

---

## `host.docker.internal`

This option:

```text
--add-host=host.docker.internal:host-gateway
```

does not create another Docker host or another Docker network.

Instead, Docker adds a hostname mapping inside the frontend container so that:

```text
host.docker.internal
```

resolves to the Docker host/gateway address.

Conceptually:

```text
Frontend Container
       |
       | host.docker.internal
       v
Docker Host
```

The use of `host-gateway` avoids hardcoding a particular Docker gateway IP address such as `172.17.0.1`.

---

## Backend URL Environment Variable

This option:

```text
-e BACKEND_URL=http://host.docker.internal:7860
```

creates the following environment variable inside the frontend container:

```text
BACKEND_URL=http://host.docker.internal:7860
```

This overrides the default backend address specified in the frontend application.

The frontend therefore sends requests to Docker host port `7860`.

The backend container was already started with:

```text
-p 7860:7860
```

so Docker forwards those requests from host port `7860` to backend container port `7860`.

---

## Codespaces Communication Path

The complete application path in Codespaces is:

```text
User Browser
     |
     | HTTPS
     v
GitHub Codespaces Forwarded Port 8501
     |
     v
Docker Host :8501
     |
     | -p 8501:8501
     v
Frontend Container :8501
     |
     | Streamlit
     | requests.post(...)
     v
host.docker.internal:7860
     |
     v
Docker Host :7860
     |
     | -p 7860:7860
     v
Backend Container :7860
     |
     v
Gunicorn
     |
     v
Flask
     |
     v
Machine Learning Model
```

The backend does not initiate a connection to the frontend.

The frontend acts as an HTTP client and initiates prediction requests to the backend.

---

# GitHub Codespaces Port Forwarding

GitHub Codespaces provides externally accessible forwarded URLs for application ports.

For this project:

```text
8501 → Streamlit frontend
7860 → Flask backend
```

Port `8501` allows the application interface to be accessed through a browser.

Port `7860` was also exposed so that external applications such as the Google Colab notebook could directly test the Flask API.

For external testing, these ports must be configured with **Public** visibility in the Codespaces Ports panel.

---

# Remote API Testing from Google Colab

The Flask backend was tested externally from Google Colab using the public Codespaces URL.

Example API status test:

```python
import requests

BACKEND_URL = "https://<codespace-name>-7860.app.github.dev".rstrip("/")

response = requests.get(BACKEND_URL)

print("Status:", response.status_code)
print("Response:", response.text)
```

---

## Single Prediction Test

```python
payload = {
    "Product_Weight": 12.5,
    "Product_Sugar_Content": "Regular",
    "Product_Allocated_Area": 0.05,
    "Product_MRP": 150.0,
    "Store_Size": "Medium",
    "Store_Location_City_Type": "Tier 2",
    "Store_Type": "Supermarket Type1",
    "Product_Id_char": "FD",
    "Store_Age_Years": 10,
    "Product_Type_Category": "Perishable"
}

response = requests.post(
    f"{BACKEND_URL}/v1/predict",
    json=payload
)

print("Status:", response.status_code)

if response.ok:
    print("Response:", response.json())
else:
    print("Response:", response.text)
```

---

## Batch Prediction Test

The batch endpoint accepts a CSV file:

```python
with open("Batch_Data_SuperKart.csv", "rb") as f:

    files = {
        "file": (
            "Batch_Data_SuperKart.csv",
            f,
            "text/csv"
        )
    }

    response = requests.post(
        f"{BACKEND_URL}/v1/predictbatch",
        files=files
    )
```

Because the batch endpoint returns CSV rather than JSON, the response is accessed using:

```python
response.content
```

For example:

```python
with open("batch_predictions.csv", "wb") as f:
    f.write(response.content)
```

---

# GitHub Container Registry

The backend and frontend Docker images were published to **GitHub Container Registry (GHCR)**.

The published images are:

```text
ghcr.io/kposcic/superkart-backend:latest
ghcr.io/kposcic/superkart-frontend:latest
```

---

## Publishing Images to GHCR

First authenticate Docker to GHCR using a GitHub Personal Access Token with the appropriate package permissions.

```bash
export CR_PAT=YOUR_GITHUB_PAT
```

```bash
echo $CR_PAT | docker login ghcr.io \
  -u kposcic \
  --password-stdin
```

The actual token should never be stored in the repository or documentation.

---

### Tag Backend Image

```bash
docker tag superkart-backend:latest \
  ghcr.io/kposcic/superkart-backend:latest
```

### Tag Frontend Image

```bash
docker tag superkart-frontend:latest \
  ghcr.io/kposcic/superkart-frontend:latest
```

Tagging does not rebuild the image.

It assigns an additional registry-qualified name to the same image.

---

### Push Backend Image

```bash
docker push ghcr.io/kposcic/superkart-backend:latest
```

### Push Frontend Image

```bash
docker push ghcr.io/kposcic/superkart-frontend:latest
```

---

# Pulling the Published Images

Because the GHCR packages are public, another Docker environment can download the images without authentication.

Backend:

```bash
docker pull ghcr.io/kposcic/superkart-backend:latest
```

Frontend:

```bash
docker pull ghcr.io/kposcic/superkart-frontend:latest
```

The images can then be verified using:

```bash
docker images
```

Example:

```text
IMAGE                                       ID
ghcr.io/kposcic/superkart-backend:latest    ...
ghcr.io/kposcic/superkart-frontend:latest   ...
```

This allows the deployment artifacts to be restored or deployed without rebuilding them from source.

---

# Running Directly from GHCR Images

Start the backend:

```bash
docker run -d \
  --name superkart-backend \
  -p 7860:7860 \
  ghcr.io/kposcic/superkart-backend:latest
```

Start the frontend in the Codespaces configuration:

```bash
docker run -d \
  --name superkart-frontend \
  -p 8501:8501 \
  --add-host=host.docker.internal:host-gateway \
  -e BACKEND_URL=http://host.docker.internal:7860 \
  ghcr.io/kposcic/superkart-frontend:latest
```

Verify the containers:

```bash
docker ps
```

Test the backend:

```bash
curl http://localhost:7860
```

Expected response:

```text
SuperKart Sales Prediction API is running
```

---

# Source Code vs Container Images

The GitHub repository and GitHub Container Registry serve different purposes.

```text
GitHub Repository
        |
        ├── Python source code
        ├── Dockerfiles
        ├── requirements files
        ├── trained model file
        └── documentation


GitHub Container Registry
        |
        ├── built backend Docker image
        └── built frontend Docker image
```

Source code is published with:

```text
git push
```

Docker images are published separately with:

```text
docker push
```

Docker image files should not be committed directly into the Git repository.

---

# Deployment Workflow

```text
Google Colab
Model Training
      |
      v
Serialized ML Pipeline
      |
      v
GitHub Repository
Source + Dockerfiles
      |
      v
GitHub Codespace
      |
      | docker build
      v
Backend + Frontend Images
      |
      | docker run
      v
Running Application
      |
      | docker push
      v
GitHub Container Registry
      |
      | docker pull
      v
Reusable Deployment Images
```

---

# Technologies Used

- Python
- pandas
- NumPy
- scikit-learn
- joblib
- Flask
- Gunicorn
- Streamlit
- Requests
- Docker
- Git
- GitHub
- GitHub Codespaces
- GitHub Container Registry
- Google Colab

---

# Business Use

The deployed application provides sales predictions for individual product/store combinations or many combinations simultaneously through batch prediction.

The predictions can support business activities such as:

- Sales forecasting
- Inventory planning
- Procurement planning
- Product allocation
- Store-level planning
- Identification of potentially high- and low-sales product/store combinations

The model predicts **sales revenue**, not physical unit demand.

Therefore, predicted sales should be treated as one input to an inventory-management process rather than directly interpreted as a reorder quantity.

Additional information such as:

- Existing inventory
- Unit demand
- Supplier lead time
- Safety stock
- Desired service level
- Supplier constraints

would be required to translate revenue forecasts into actual replenishment quantities.

---

# Summary

This project demonstrates the complete machine learning deployment workflow:

```text
Train Model
    ↓
Serialize Model
    ↓
Create Flask REST API
    ↓
Create Streamlit Frontend
    ↓
Containerize Both Applications
    ↓
Test Locally
    ↓
Push Source to GitHub
    ↓
Rebuild and Test in GitHub Codespaces
    ↓
Test API Remotely
    ↓
Publish Docker Images to GHCR
    ↓
Pull and Run Images from Registry
```

The resulting deployment separates the machine learning model, backend API, frontend interface, source repository, and container registry into distinct components that can be developed, tested, and deployed independently.
