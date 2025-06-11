# Use a stable, official Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app's source code into the container
COPY . .

# Expose the port that Streamlit will run on (Hugging Face default is 7860)
EXPOSE 7860

# Set the healthcheck to ensure the app is running
HEALTHCHECK --interval=10s --timeout=3s \
  CMD curl --fail http://localhost:7860/_stcore/health

# The command to run when the container starts
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
