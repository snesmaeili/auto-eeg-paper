FROM python:3.10-slim

# System deps for MNE & plotting
RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    libfftw3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose Jupyter
EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''"]
