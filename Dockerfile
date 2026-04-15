FROM python:3.12-slim
WORKDIR /main
#This line of code is saying copy from the same place as where the Dockerfile is found, into an app directory
COPY . .
RUN pip install fastapi uvicorn[standard]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]