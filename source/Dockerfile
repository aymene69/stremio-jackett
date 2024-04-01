FROM python:3.12.2

WORKDIR /app

# This is to prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-level", "critical", "--reload"]