FROM python:3.11-slim

EXPOSE 5000

COPY . /src
RUN pip install /src && rm -rf /src && pip cache purge

ENTRYPOINT ["egon-server"]
