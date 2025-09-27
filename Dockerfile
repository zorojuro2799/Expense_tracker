# Use full Debian-based Python image
FROM python:3.10-bullseye

# Install system dependencies including Tesseract
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    ca-certificates \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit environment variables
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV PORT=10000

# Expose the port
EXPOSE 10000

# Start Streamlit
CMD ["streamlit", "run", "MExpenseTracker.py", "--server.port", "10000"]
