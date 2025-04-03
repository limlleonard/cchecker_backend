# syntax=docker/dockerfile:1

FROM python:3.12-alpine
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8001
CMD ["uvicorn", "back.asgi:application", "--host", "0.0.0.0", "--port", "8001"]
# docker run -dp 127.0.0.1:8000:8000 cchecker_backend:tag1
# docker build -t cchecker_backend:tag2_stateless .
# docker run -dp 127.0.0.1:8001:8001 cchecker_backend:tag2_stateless

# expose 5001 is optional metadata and doesn't actively do anything except document the port.
# docker run 5001 should match the Flask port , because it links to the port inside the container where the app listens.
# --host 0.0.0.0: Makes the app listen on all network interfaces inside the container (needed for Docker).
# --port 8000: The app will be exposed on port 8000 inside the container.

# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
