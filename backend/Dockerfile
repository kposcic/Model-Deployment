# Start from a lightweight Linux image containing Python 3.12
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file first
COPY requirements.txt .

# Install the Python dependencies inside the image
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application and trained model into the image
COPY app.py .
COPY superkart_sales_model_pipeline.joblib .

# Document that the application listens on port 7860
EXPOSE 7860

# Start the Flask application using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]