FROM python:3.11-slim

# Installation de Java (requis pour Spark)
RUN apt-get update && apt-get install -y default-jre wget && apt-get clean

# Installation de Spark et PySpark
RUN pip install --no-cache-dir pyspark

# Téléchargement du connecteur MySQL JDBC
RUN wget https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.3.0/mysql-connector-j-8.3.0.jar -P /opt/spark/jars/

# Copie du projet
WORKDIR /app
COPY . /app

# Point d'entrée
CMD ["python3", "mainpySpark.py"]