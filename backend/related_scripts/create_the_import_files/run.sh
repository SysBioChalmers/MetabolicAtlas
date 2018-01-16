# get the ensembl to uniprot mapping directly from EnsMart, supply version number!
python getEnsemblData.py -v 82


# get the annotations from enzymes as based on the uniprot data
# wget ftp://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/complete/uniprot_sprot.dat.gz

python getUniProtData.py -s "_HUMAN" -f uniprot_sprot.dat --get "Function" > uniprot.human.function.tab
python getUniProtData.py -s "_HUMAN" -f uniprot_sprot.dat --get "Keyword" > uniprot.human.keywords.tab
python getUniProtData.py -s "_HUMAN" -f uniprot_sprot.dat --get "DatabaseCrossReferences" > uniprot.human.databasecrossreferences.tab
python getUniProtData.py -s "_HUMAN" -f uniprot_sprot.dat --get "Description" > uniprot.human.names.tab
python getUniProtData.py -s "_HUMAN" -f uniprot_sprot.dat --get "EC" > uniprot.human.EC.tab
python getUniProtData.py -s "_HUMAN" -f uniprot_sprot.dat --get "CatalyticActivity" > uniprot.human.CatalyticActivity.tab


# get the Brenda Tissue Ontology
curl http://data.bioontology.org/ontologies/BTO/submissions/33/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb --output BTO.OBO

perl getBTO.pl --findThis all > BTO.tab
