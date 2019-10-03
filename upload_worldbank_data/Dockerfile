FROM python:2.7
MAINTAINER Amelia Snyder <amelia.snyder@wri.org>

# install core libraries
RUN apt-get update && pip install -U pip

# install application libraries
RUN pip install requests
RUN pip install pandas
RUN pip install boto3

# set name
ARG NAME=upload-world-bank
ENV NAME ${NAME}

# copy the application folder inside the container
RUN mkdir -p /opt/$NAME/data
WORKDIR /opt/$NAME/
COPY contents .

RUN useradd -r $NAME
RUN chown -R $NAME:$NAME /opt/$NAME
VOLUME /opt/$NAME/data
USER $NAME
ENV PYTHONPATH /src

CMD ["python", "main.py"]
