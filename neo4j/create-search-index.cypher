CALL db.index.fulltext.createNodeIndex(
 	"fulltext",
 	["CompartmentState", "Compartment", "MetaboliteState", "Metabolite", "CompartmentalizedMetabolite", "SubsystemState", "Subsystem", "ReactionState", "Reaction", "GeneState", "Gene", "PubMedReference"],
 	["id", "name", "letterCode", "alternateName", "synonyms", "description", "formula", "function", "pubMedID"]
)
