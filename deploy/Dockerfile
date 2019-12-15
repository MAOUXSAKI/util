FROM 10.32.233.112/library/python:3.7-alpine
RUN pip install pyyaml
COPY entrypoint.sh /root/
CMD sh /root/entrypoint.sh
COPY init.py /root/
