# SuperKart Sales Prediction - Model Deployment

## Project Overview

SuperKart is a retail chain operating supermarkets and food marts across different city tiers. The objective of this project is to predict product-store sales revenue and deploy the trained machine learning model as an application that can support sales forecasting and inventory planning.

The solution consists of two independently containerized components:

- **Backend:** Flask REST API served by Gunicorn
- **Frontend:** Streamlit web application

The trained machine learning pipeline is serialized using `joblib` and loaded by the backend API.

The project was developed and tested locally and then rebuilt and tested in a GitHub Codespace. The final Docker images are published to GitHub Container Registry (GHCR).

---

## Architecture

```text
User Browser
     |
     | HTTP/HTTPS
     v
Streamlit Frontend
Port 8501
     |
     | REST API request
     v
Flask / Gunicorn Backend
Port 7860
     |
     v
Serialized ML Pipeline
     |
     v
Predicted Sales
