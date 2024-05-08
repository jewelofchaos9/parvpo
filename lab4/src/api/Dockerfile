FROM python:3.12-slim

COPY ./requirments.txt .
RUN pip install -r requirments.txt

COPY ./server.py .

CMD ["python3", "server.py"]
