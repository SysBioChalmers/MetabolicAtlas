import requests, json, sys

enzymeName=sys.argv[1];
url = "http://130.238.29.191/api/v1/enzymes/"+enzymeName+"/connected_metabolites?include_expressions=true"
response = requests.get(url, auth=requests.auth.HTTPBasicAuth('hma','K5U5Hxl8KG'))
data = json.loads(response.text)
#print(data) # this is a dictionary!
r = data["reactions"]
for rr in r:
    #print(rr["reaction_id"])
    for rec in rr["reactants"]:
        #print(rec["short_name"]);
        print("for the Enzyme "+enzymeName," metabolite '"+rec["short_name"]+"' was affected in reaction '"+rr["reaction_id"]+"'")
