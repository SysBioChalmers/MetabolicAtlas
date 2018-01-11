#!/usr/bin/python

import re, csv, argparse

# parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-s', dest='species', help="which species? default _HUMAN", type=str, default="_HUMAN")
parser.add_argument('-f', dest='file', help="which file? default uniprot_sprot.dat", type=str, default="uniprot_sprot.dat");
parser.add_argument('--get', dest='outType', help="What type of data should be retrived", type=str, default="Function");
args = parser.parse_args()

# print the headers of the output so I know what is what...
ColumnHeader = args.outType
if(args.outType == "Description"):
    ColumnHeader = "RecommendedName\tShortName\tGeneSymbol"
print "UniProtID\tUniProtACC\t"+ColumnHeader

# parse the uniprot data
# TODO get altname
with open(args.file, 'r') as f:
  id = ""
  mainACC = ""
  foundStartCC = False
  ccLines = ""
  CC = []
  EC = []
  function = []
  keywords = [] #empty list
  recName = ""; shortName = ""; geneSymbol = "";
  containsFound = False
  for row in f:
    if row[0:2] == "ID" or row[0:2] == "//":
        # first test if a rec name but not a short name was specified for the previous one...
        if args.outType == "Description" and recName:
            print id + "\t" + mainACC + "\t" + recName + "\t" + shortName + "\t"
            recName = ""; shortName = ""; geneSymbol = "";
        elif args.outType == "EC" and mainACC:
            print id + "\t" + mainACC + "\t" + "; ".join([e.strip() for e in EC])
            EC = []
        elif args.outType == "CatalyticActivity" and mainACC:
            print id + "\t" + mainACC + "\t" + "; ".join([
                e.replace("  ", " ").replace("- ", "-")
                .replace(", ", ",").strip('.').strip() 
                for e in CC])
            CC = []
        elif args.outType == "Function" and mainACC:
            print id + "\t" + mainACC + "\t" + ". ".join([
                e.replace("  ", " ").replace("- ", "-")
                .replace(", ", ",").strip('.').strip() 
                for e in function])
            function = []
        if row.find(args.species) > -1:
            id = row[3:row.find(args.species)+len(args.species)]
            id = id.strip()
        else:
            id = ""
        mainACC = ""
        containsFound = False
        geneSymbol = ""
    elif id:
        #print("Have an id "+id+" and now looking at line "+row)
        # when I know I have the right species, bother looking at the other lines...
        if row[0:2] == "AC":   #AC   P31946; A8K9K2; E1P616;
            if not mainACC:
                mainACC = re.sub(r";.*", "", row[5:]).strip()
        elif args.outType == "Description" and row[0:2] == "DE":
            #DE   AltName: Full=Transient receptor potential cation channel subfamily P member 2 {ECO:0000312|MGI:MGI:1099818};
            #DE   RecName: Full=Acid-sensing ion channel 1;
            name = re.sub(r"^([A-Za-z]|:| )*=","", re.sub(r"(;|{ECO.*)$", "", row[5:].strip()))
            name = re.sub(r";","", name)
            if row.find("RecName") > -1 and not containsFound:
                recName = name
            elif row.find("Short") > -1 and recName:
                #print id + "\t" + mainACC + "\t" + recName + "\t" + name
                #recName = ""
                shortName= name
            elif row.find("Contains") > -1:
                containsFound = True
        elif args.outType == "Description" and row[0:2] == "GN":
            #GN   ORFNames=FV3-001R;     # some of the non-human ones
            #GN   Name=YWHAB;            # the most common example
            # some of the uniprot identifiers have synonyms as well... (two possibilities for format!)
            #GN   Name=TRMT5 {ECO:0000255|HAMAP-Rule:MF_03152};
            #GN   Synonyms=KIAA1393, TRM5 {ECO:0000255|HAMAP-Rule:MF_03152};
            # Name=HSD3B1; Synonyms=3BH, HSDB3A;
            # but there are some examples in which there are multiple gene symbols
            #GN   Name=AGAP4 {ECO:0000312|HGNC:HGNC:23459};
            #GN   Synonyms=AGAP8 {ECO:0000312|HGNC:HGNC:23459},
            #GN   CTGLF1 {ECO:0000312|HGNC:HGNC:23459},
            #GN   CTGLF5 {ECO:0000312|HGNC:HGNC:23459},
            #GN   MRIP2 {ECO:0000312|EMBL:AAL10290.1};
            if not geneSymbol:
                geneSymbol = re.sub(r"^.*Name(s|)=","", re.sub(r"(;.*|{ECO.*)$", "", row[3:])).strip()
                print id + "\t" + mainACC + "\t" + recName + "\t" + shortName + "\t" + geneSymbol
                recName = ""; shortName = "";
        elif args.outType == "EC" and row[0:2] == "DE" and row.find("EC=") > -1:
            EC.append(re.sub(r"\s?{ECO.*", "", row[row.find("EC=")+3:].strip().strip(';')))
        elif args.outType == "Keyword" and row[0:2] == "KW":
            #KW   Complete proteome; Reference proteome.
            temp = row[5:].strip().split("; ")
            # keywords = keywrods + temp # concatenate lists
            for k in temp:
                print id + "\t" + mainACC + "\t" + re.sub(r"(;|\.)$", "", k)
        elif args.outType == "DatabaseCrossReferences" and row[0:2] == "DR":
            #DR   TCDB; 1.A.1.5.7; the voltage-gated ion channel (vic) superfamily
            print id + "\t" + mainACC + "\t" + row[5:].strip()
        # finally handle the comment lines (eg the CC liens)
        elif row.find("CC") == 0 and \
            (args.outType == "Function" or args.outType == "CatalyticActivity"):
            if row[0:18] == "CC   -!- FUNCTION:" and args.outType == "Function":
                if foundStartCC:
                    function.append(re.sub(r"\s?{ECO.*", "", ccLines))
                foundStartCC = True
                ccLines = row[19:].strip()
            elif row[0:28] == "CC   -!- CATALYTIC ACTIVITY:" and args.outType == "CatalyticActivity":
                if foundStartCC:
                    CC.append(re.sub(r"\s?{ECO.*", "", ccLines))
                foundStartCC = True
                ccLines = row[29:].strip()
            elif not re.search("CC   -!-", row) and foundStartCC:
                ccLines += " " + row[9:].strip()
            elif foundStartCC and row.find("-!-") == 5:
                #print id + "\t" + mainACC + "\t" + re.sub(r"{ECO.*", "", ccLines)
                if args.outType == "CatalyticActivity":
                    CC.append(re.sub(r"\s?{ECO.*", "", ccLines))
                else:
                    function.append(re.sub(r"\s?{ECO.*", "", ccLines))
                foundStartCC = False; # ccLines = ""
