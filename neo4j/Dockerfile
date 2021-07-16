FROM neo4j:4.2.5
ARG NEO4J_USERNAME
ARG NEO4J_PASSWORD

RUN rm -r /var/lib/neo4j/data
COPY import ./import
COPY import.sh .
RUN ./import.sh
