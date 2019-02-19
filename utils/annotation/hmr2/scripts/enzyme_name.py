
import db_tools
import tools

con = db_tools.connect(db_name='hmr2')

cur = db_tools.execute(con, "select * from reaction_component where component_type = 'e'")

res = {}
for r in cur.fetchall():
    r = list(r)
    print (r)
    ensembl_id = r[2]
    name = r[1]
    if ensembl_id in res:
        print("Error: id '%s' already in dict" % (ensembl_id))
        exit(1)
    res[ensembl_id] = { 'name': name }


enzyme_file = '/project/annotation/hmr2/ENZYMES.txt'
ld = tools.merge_values(enzyme_file, res)
tools.write_dicts_to_file(ld, enzyme_file)