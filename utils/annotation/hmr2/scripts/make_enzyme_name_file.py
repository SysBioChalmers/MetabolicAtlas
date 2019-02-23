import db_tools
import tools

con = db_tools.connect(db_name='hmr2')
cur = db_tools.execute(con, "select id from reaction_component where component_type = 'e'")

IDS = set()
for r in cur.fetchall():
    eid = r[0]
    if eid in IDS:
        print("Error: id '%s' already in dict" % (eid))
        exit(1)
    IDS.add(eid)

res = {}
with open('/project/annotation/hmr2/scripts/enzyme_name_human.txt', 'r') as fh:
    for line in fh:
        line = line.split('\t')
        eid = line[0]
        if eid in IDS:
            res[eid] = {'ID': eid, 'name': line[4]}

enzyme_file = '/project/annotation/hmr2/ENZYMES.txt'
ld = tools.merge_values(enzyme_file, res)
tools.write_dicts_to_annotation_file(ld, enzyme_file)
