FROM python:3.11

WORKDIR /jarvis
COPY . .

RUN pip install asyncio
RUN pip install beautifulsoup4
RUN pip install discord.py
RUN pip install characterai
RUN pip install requests
RUN pip install python-dotenv

CMD ["python", "main.py"]
