FROM python:3.11-slim

EXPOSE 5000

COPY . /src
RUN pip install /src && rm -rf /src && pip cache purge

ENV EGON_SERVER_HOST="0.0.0.0"
ENTRYPOINT ["egon-server"]
