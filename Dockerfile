# Base Image
FROM python:3.11.9@sha256:e453eb723bc8ecac7a797498f9a5915d13e567620d48dcd3568750bac3b59f31

# Set the working directory
WORKDIR /src

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY app/ app/

# Run the application
CMD python manage.py runserver 0.0.0.0:8000
