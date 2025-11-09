FROM python:3.12-slim

WORKDIR /backend

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY bank_iq/api_payloads ./api_payloads
COPY bank_iq/accounts ./accounts
COPY bank_iq/analytics ./analytics
COPY bank_iq/bank_iq ./bank_iq
COPY bank_iq/banks ./banks
COPY bank_iq/core ./core
COPY bank_iq/exports ./exports
COPY bank_iq/financials ./financials
COPY bank_iq/indicators ./indicators
COPY bank_iq/reports ./reports
COPY bank_iq/manage.py ./manage.py

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]