# This is the python image
FROM python:3.11-slim

# Use UV for the venv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Making a dir for my code
WORKDIR /app

# Pull the requirements
COPY requirements.txt .

# run the req file 
RUN uv pip install --system --no-cache -r requirements.txt


# Copy my code

COPY . .

# Expose where my app will run
# Port mapping 

EXPOSE 8501


# How to run my app 
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]