FROM python:3.11-slim

# 1. Variables d'environnement
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# 2. Installation de Java (version par défaut stable)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Le reste de ton Dockerfile...
WORKDIR /app
RUN mkdir -p /app/jars
RUN wget https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.3.0/mysql-connector-j-8.3.0.jar -O /app/jars/mysql-connector-j.jar
RUN pip install --no-cache-dir pyspark
COPY . /app
CMD ["python3", "main.py"]