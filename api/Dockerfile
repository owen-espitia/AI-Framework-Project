FROM python:3.12-slim
WORKDIR /main
COPY api/main.py .
COPY api/dal.py .
COPY api/models.py .
COPY api/model.py .
COPY api/simple_classifier.pth .
COPY requirements.txt .
ENV MODEL_PATH=/main/simple_classifier.pth
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
#uvicorn api.main:app --reload