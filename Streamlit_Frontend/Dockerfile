# Frontend/Dockerfile

FROM python:3.10.8-slim

RUN mkdir -p app/frontend

COPY Streamlit_Frontend app/frontend

WORKDIR /app/frontend

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["sh", "-c", "streamlit run Hello.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
