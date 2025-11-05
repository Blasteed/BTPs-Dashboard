FROM python:3.14

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD python -m streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
