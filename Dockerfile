FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install uv && uv pip install --system .
CMD ["python", "-m", "api_chat.main"]