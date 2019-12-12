FROM python:3.7
RUN pip install pyyaml
COPY init.py /root/
COPY entrypoint.sh /root/
CMD sh /root/entrypoint.sh
