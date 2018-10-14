
FROM python:2.7

MAINTAINER YQCHEN

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD . /code/

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends dialog \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd 
COPY sshd_config /etc/ssh/
EXPOSE 8000 2222

RUN apt-get update -y \
    && apt-get install -y praat \
    && apt-get install -y python-dev default-libmysqlclient-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY init.sh /usr/local/bin/

RUN chmod u+x /usr/local/bin/init.sh
ENTRYPOINT ["init.sh"]
