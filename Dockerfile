FROM python:3.11-slim

EXPOSE 5000

COPY . /src
RUN mkdir /var/log/egon_api_server && pip install /src && rm -rf /src && pip cache purge

# COnfigure the applciation
ENV EGON_SERVER_HOST="0.0.0.0"
ENV EGON_LOG_PATH="/var/log/egon_api_server/server.log"

ENTRYPOINT ["egon-server"]
