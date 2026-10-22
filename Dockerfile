FROM python:3.11-slim
WORKDIR /app
COPY . /app
EXPOSE 10000
CMD ["python", "server.py"]
