FROM neo4j:4.1.1 as neo4jdbdump

ARG NEO4J_USERNAME
ARG NEO4J_PASSWORD

COPY import ./import
RUN ./import/import.sh


FROM neo4j:4.1.1

COPY --from=neo4jdbdump /db.dump /db.dump
