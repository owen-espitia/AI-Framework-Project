FROM python:3.12-slim
WORKDIR /main
COPY api/main.py .
COPY api/dal.py .
COPY api/models.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#uvicorn api.main:app --reload