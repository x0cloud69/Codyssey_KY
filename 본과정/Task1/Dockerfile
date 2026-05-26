FROM ubuntu:latest

RUN apt update && \
    apt install -y openssh-server vim iproute2

RUN mkdir -p /run/sshd

RUN sed -i 's/#Port 22/Port 20022/' /etc/ssh/sshd_config

RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 20022

CMD ["/usr/sbin/sshd", "-D"]