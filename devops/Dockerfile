FROM python:3.9-slim AS builder

WORKDIR /src

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python setup.py sdist bdist_wheel

# Production
FROM python:3.9-slim

WORKDIR /src

RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY --from=builder /src/dist/*.whl .
RUN pip install *.whl

CMD kopf run -m axop --liveness=http://0.0.0.0:5000/healthz -A --peering=axoniq-operator
