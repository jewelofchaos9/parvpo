FROM python:3.12-slim

COPY ./requirments.txt .
RUN pip install -r requirments.txt

COPY ./worker.py .

CMD ["python3", "worker.py"]
