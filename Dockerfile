FROM mcr.microsoft.com/playwright:v1.15.0-focal

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN playwright install

COPY ./app /app
WORKDIR /

EXPOSE 80
EXPOSE 10000
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "10000"]