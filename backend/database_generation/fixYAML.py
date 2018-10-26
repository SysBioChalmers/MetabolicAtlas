import sys
import os

# add double quote around "name" values
# remove all "- pmid" lines
# remove "- annotation: !!omap" lines if there was only pmid as annotation and it has been removed

os.system('sed -re \'s/    - name:\s*([^"]+)$/    - name: "\\1"/g\' %s > %s.tmp && mv %s.tmp %s' % (sys.argv[1], sys.argv[1], sys.argv[1], sys.argv[1]))

f = open(sys.argv[1],"r")
lines = f.readlines()
f.close()

f = open(sys.argv[1], "w")
in_pmid = False
for line in lines:
    if not line.startswith("      - pmid:"):
        if not in_pmid:
            f.write(line)
        elif not line.startswith("        - "):
            in_pmid = False
            f.write(line)
    else:
        in_pmid = True
f.close()

f = open(sys.argv[1],"r")
lines = f.readlines()
f.close()

f = open(sys.argv[1], "w")
for i, line in enumerate(lines):
    if line.strip() == "- annotation: !!omap" and lines[i+1].strip() == "- confidence_score: 0":
        continue
    f.write(line)
f.close()