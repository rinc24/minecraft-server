FROM python:3.12-rc-slim-buster
WORKDIR /
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py /
COPY bot.py /
CMD ["python", "-u", "/main.py"]
