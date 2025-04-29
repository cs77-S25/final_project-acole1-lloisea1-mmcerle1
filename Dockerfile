FROM python:3.12.10-slim-bullseye

# WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=6000"]


#docker build --tag my-cool-project .

