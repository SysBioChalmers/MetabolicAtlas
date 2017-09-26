#!/usr/bin/python

import sys, argparse, os

parser = argparse.ArgumentParser()
parser.add_argument('-v', dest='version', help="which ensembl version to use? default current", default=89, type=int)
parser.add_argument('-a', dest='attributes', help="which columns to get, default hgnc_symbol, uniprot_swissprot", type=str)
parser.add_argument('-s', dest='os', help="which OS, mac or linux? will influence the command to run", default='mac', type=str)
parser.add_argument('-p', dest='only_print', action='store_true', default=False);
parser.add_argument('-o', dest='organism', help="which organism, default human", default='hsapiens', type=str)
args = parser.parse_args()
attributes=['hgnc_symbol','uniprot_swissprot'];
if((args.attributes is not None) and (len(args.attributes)>0)):
	attributes = args.attributes.split(",")
outputFile="downloadedFiles/ensembl" + str(args.version) + "_" + "_".join(attributes) + "."+args.organism+".tab"
outputFile.replace("_1006", "") # for GO attributes...
outputFile.replace("_1003", "") # for GO attributes...


def versionMap(v):
 	# http://www.ensembl.org/biomart/martservice
	if(v==89):
		return 'http://sep2015.archive.ensembl.org/biomart/martservice'
	elif(v==82):
		return 'http://sep2015.archive.ensembl.org/biomart/martservice'
	elif(v==81):
		return 'http://jul2015.archive.ensembl.org/biomart/martservice'
	elif(v==78):
		return 'http://dec2014.archive.ensembl.org/biomart/martservice'
	elif(v==67):
		return 'http://may2012.archive.ensembl.org/biomart/martservice'
	elif(v==54):
		return 'http://may2009.archive.ensembl.org/biomart/martservice'
	else:
		sys.exit("\n*******************************\nError:\n\tNot a known version map\n*******************************\n");

def getXML(attributes):
	xml="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query virtualScheme="default" formatter="TSV" header="1" uniqueRows = "1">
	<Dataset name="""
	xml+="\""+args.organism+"_gene_ensembl\""
	xml+=""" interface="default">
		<Attribute name="ensembl_gene_id" />"""
	for a in attributes:
		xml = xml + '<Attribute name="' + a + '" />'
	xml=xml+"""
</Dataset>
</Query>"""
	return xml

def getData(oFile, ver, att):
	mart=versionMap(ver)
	if args.os == "mac":
		# for mac where curl is available
		cmd='curl --output ' + oFile + ' --data-urlencode query=\'' + getXML(att) + '\' ' + mart + '/results'
	elif args.os == "linux":
		# for linux where wget is available
		cmd='wget -O ' + oFile + ' \'' + mart + '?query=' + getXML(att) + '\''
	else:
		print("not a recognised OS, should have been mac or linux")
		sys.exit(0)
	if args.only_print:
		print(cmd)
	else:
		os.system(cmd)


getData(outputFile, args.version, attributes)
