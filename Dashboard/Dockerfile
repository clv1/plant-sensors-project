FROM python:3.11

WORKDIR /dashboard

ENV ACCEPT_EULA=Y

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends curl gcc g++ gnupg unixodbc-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends --allow-unauthenticated msodbcsql17 mssql-tools

RUN pip3 install --no-binary :all: pyodbc

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY dashboard.py .

COPY dashboard_functions.py .

EXPOSE 8501

CMD streamlit run dashboard.py