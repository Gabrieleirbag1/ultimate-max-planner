FROM python:3.12-alpine
WORKDIR /app
COPY . /app
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["src/server.py"]