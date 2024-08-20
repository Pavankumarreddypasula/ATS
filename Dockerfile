FROM python:3.12-slim

# Install Poppler utilities
RUN apt-get update && apt-get install -y poppler-utils

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . /app
WORKDIR /app

# Command to run the Streamlit app
CMD ["streamlit", "run", "app.py"]
