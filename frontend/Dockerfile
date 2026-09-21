# Start from lightweight Linux image with Python 3.12
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy dependency file first
COPY requirements.txt .

# Install frontend dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Streamlit application
COPY app.py .

# Document the Streamlit port
EXPOSE 8501

# Start the Streamlit web application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]