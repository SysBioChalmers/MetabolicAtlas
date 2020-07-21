FROM neo4j:4.1.1

ARG NEO4J_USERNAME
ARG NEO4J_PASSWORD

RUN rm -r /var/lib/neo4j/data
COPY ./import /var/lib/neo4j/import
COPY ./create-search-index.cypher /var/lib/neo4j/import
COPY ./import.sh /
RUN chmod +x /import.sh
RUN /import.sh
