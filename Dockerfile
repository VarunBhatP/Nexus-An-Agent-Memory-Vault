# 1. Base Image: Use a lightweight Python version
# "slim" means it has Python but cuts out junk to keep file size small (100MB vs 1GB)
FROM python:3.11-slim

# 2. Set the "Working Directory" inside the container
# This is like doing "cd /code" inside the mini-computer
WORKDIR /code

# 3. Cache Optimization: Copy ONLY requirements first
# Why? Docker caches layers. If you change code but not requirements, 
# it won't re-download pip packages (saves huge time).
COPY ./requirements.txt /code/requirements.txt

# 4. Install Dependencies
# --no-cache-dir keeps the image small by deleting download cache
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Copy the Application Code
# This puts your app folder inside the container
COPY ./app /code/app

# 6. The Start Command
# "0.0.0.0" is CRITICAL. It means "listen on all network interfaces"
# If you use 127.0.0.1, Docker hides the app from the outside world.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
