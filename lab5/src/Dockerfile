FROM python:3.12-slim

COPY ./requirments.txt .
RUN pip install -r requirments.txt

COPY ./main.py .
COPY ./ips.txt .

CMD ["python3", "main.py"]
