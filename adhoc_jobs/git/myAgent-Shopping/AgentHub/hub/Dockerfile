FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml ./
RUN pip install -e "."

# Copy hub code
COPY hub/ ./hub/
COPY agora/ ./agora/

# Expose MQTT ports
EXPOSE 1883 8083

CMD ["python", "hub/main.py"]
