FROM python:3.8.5-slim-buster
WORKDIR \server_api_test
RUN pip3 install urllib3 pytest subprocess.run regex
COPY . .
CMD [ "/bin/bash" ]