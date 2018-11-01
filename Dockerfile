# Build an image starting with the Python 3.7 image
FROM python:3.7

# Add the current directory . into the path /app in the image
ADD . /app

# Set the working directory to /app
WORKDIR /app

# Install the Python dependencies
RUN pip install -r requirements.txt

# Set the default command for the container to python app.py
CMD ["python", "app.py"]