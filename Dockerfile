# Base Image
FROM python3.11

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
