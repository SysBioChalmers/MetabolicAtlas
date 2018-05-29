




def save_pathway(database, name, eid):
    sys = "Other"
    # assume that its a pathway UNLESS the name matches one of the below, or starts with 'Transport'
    # because then I will consider it a 'collection of reactions' rather than a pathway
    collec = dict([
            ("Isolated", 1),("Miscellaneous",1),("Pool reactions",1),
            ("isolated",1),("Exchange reactions ",1),("Artificial reactions",1),
            ("ABC transporters",1),("Other amino acid",1)
        ])
    aa = dict([
            ("Pyrimidine metabolism",1),("Alanine, aspartate and glutamate metabolism",1),
            ("Arginine and proline metabolism",1),("Glycine, serine and threonine metabolism",1),
            ("Lysine metabolism",1),("Tyrosine metabolism",1),("Valine, leucine, and isoleucine metabolism",1),
            ("Cysteine and methionine metabolism",1),("Thiamine metabolism",1),s
            ("Tryptophan metabolism",1),("Histidine metabolism",1)
        ]);
    vitamins = dict([
            ("Folate metabolism",1),("Biotin metabolism",1),("Retinol metabolism",1),
            ("Riboflavin metabolism",1)
        ])

    if name.startswith("Fatty acid") or name.startswith("Beta oxidation"):
        sys = "Fatty acid"
    elif name in aa:
        sys = "Amino Acid metabolism"
    elif name in vitamins or name.startswith("Vitamin"):
        sys = "Vitamin metabolism"
    elif name.startswith("Glycosphingolipid"):
        sys = "Glycosphingolipid biosynthesis/metabolism"
    elif name.startswith("Carnitine shuttle"):
        sys = "Carnitine shuttle"
    elif name.startswith("Cholesterol biosynthesis"):
        sys = "Cholesterol biosynthesis"
    elif "metabolism" in name:
        sys = "Other metabolism"
        if name == "Fructose and Mannose metabolism":
            name = "Fructose and mannose metabolism"
    elif name in collec or name.startswith("Transport"):
        sys = "Collection of reactions"

    pathway = Subsystem(name=name, system=sys, external_id=eid, description="")
    #FIXME add subsystem description
    pathway.save(using=database)
    return pathway