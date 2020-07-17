FROM neo4j:4.1.0

ARG NEO4J_USERNAME
ARG NEO4J_PASSWORD

COPY ./import /var/lib/neo4j/import
COPY ./create-search-index.cypher /var/lib/neo4j/import
COPY ./import.sh /
RUN chmod +x /import.sh
RUN /import.sh
