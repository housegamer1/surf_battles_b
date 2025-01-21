FROM python:3.12-slim AS builder

# Create and change to the app directory.
WORKDIR /app

# Retrieve application dependencies.

COPY requirements.txt ./
RUN python3 -m venv venv
ENV PATH=/app/venv/bin/:$PATH

RUN pip install -r requirements.txt

# Copy local code to the container image.
COPY . ./

FROM gcr.io/distroless/python3

## Copy the binary to the production image from the builder stage.
COPY --from=builder /app /app

WORKDIR /app

ENV ENVIRONMENT="production"
ENV PYTHONUNBUFFERED=1
ENV PORT="5000"
ENV PYTHONPATH=/app/venv/lib/python3.12/site-packages
ENV PATH=/app/venv/bin/:$PATH

EXPOSE 5000

## Run the web service on container startup.
CMD ["main.py"]
