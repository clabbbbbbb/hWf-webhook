FROM python:3.10.12-slim
ADD main.py .
RUN pip install schedule requests supabase
CMD ["python", "-u", "main.py"]
