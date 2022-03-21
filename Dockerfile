FROM python:3.10
RUN pip3 install -r requirements.txt
CMD ["python", "bot.py"]