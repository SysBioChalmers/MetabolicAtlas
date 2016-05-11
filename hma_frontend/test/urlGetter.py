import requests, json, sys

mainURL = "http://130.238.29.191/api/v1/"
enzymeName=sys.argv[1];

def getJSON(url):
    print("URL to retrieve from is: "+url); # open this in the web-page to see the JSON
    response = requests.get(url, auth=requests.auth.HTTPBasicAuth('hma','K5U5Hxl8KG'))
    data = json.loads(response.text)
    #print(data) # this is a dictionary - use this to see the structure of the JSON
    return(data)

# deal with reactions
url = mainURL+"enzymes/"+enzymeName+"/connected_metabolites"
data = getJSON(url)
r = data["reactions"]
for rr in r:
    #print(rr["reaction_id"])
    for rec in rr["reactants"]:
        #print(rec["short_name"]);
        print("for the Enzyme "+enzymeName," metabolite '"+rec["short_name"]+"' was affected in reaction '"+rr["reaction_id"]+"'")

#deal with expression data
print("The Expression Levels for Enzyme "+enzymeName);
url = mainURL+"enzymes/"+enzymeName+"/connected_metabolites?include_expressions=true&tissue=appendix&expression_type=Staining"
data = getJSON(url)
e = data["expressions"]
for exp in e:
    print(exp["tissue"]+"\t"+exp["expression_type"]+"\t"+exp["cell_type"]+"\t"+exp["level"])
