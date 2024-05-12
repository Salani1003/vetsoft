# Base Image
FROM python:3.11.9-slim@sha256:6d2502238109c929569ae99355e28890c438cb11bc88ef02cd189c173b3db07c

# Set the working directory
WORKDIR /src

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY /app/ /src/app/
COPY /vetsoft/ /src/vetsoft/
COPY manage.py /src/


# Run migrations when creating the container
RUN python manage.py migrate

# Run the application
CMD python manage.py runserver 0.0.0.0:8000
