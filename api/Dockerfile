FROM python:3.12-slim
WORKDIR /main
COPY api/main.py .
COPY api/dal.py .
COPY api/models.py .
COPY api/model_training.py .
COPY api/refined_simple_classifier.pth .
COPY requirements.txt .
ENV MODEL_PATH=/main/refined_simple_classifier.pth
RUN pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]