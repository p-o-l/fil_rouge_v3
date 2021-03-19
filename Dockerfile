FROM python:3.9.2
COPY . .

ADD aws aws/
ENV AWS_SHARED_CREDENTIALS_FILE=/aws/credentials
ENV AWS_CONFIG_FILE=/aws/config
ENV AWS_PROFILE=csloginstudent

RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main.py"]