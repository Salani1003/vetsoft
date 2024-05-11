# Base Image
FROM python:3.11.9

# Set the working directory
WORKDIR /src

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application
COPY /app/ /src/app/
COPY /vetsoft/ /src/vetsoft/
COPY manage.py /src/

# Run the application
CMD python manage.py runserver 0.0.0.0:8000
