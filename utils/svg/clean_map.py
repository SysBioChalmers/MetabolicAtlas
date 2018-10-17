import os
import glob
import re
import sys
import shutil
import argparse

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('input_dir', action="store")
parser.add_argument('output_dir', action="store")
parser.add_argument('--skip-svgo', action="store_true", default=False, dest="skip_svgo")
parser.add_argument('--skip-rm-title', action="store_true", default=False, dest="skip_rm_title")
parser.add_argument('--skip-sed', action="store_true", default=False, dest="skip_sed")
parser.add_argument('--skip-cp', action="store_true", default=False, dest="skip_clean_path")
parser.add_argument('--skip-rs', action="store_true", default=False, dest="skip_rs")

results = parser.parse_args()
input_dir = results.input_dir
output_dir = results.output_dir
skip_svgo = results.skip_svgo
skip_rm_title = results.skip_rm_title
skip_sed = results.skip_sed
skip_clean_path = results.skip_clean_path
skip_rs = results.skip_rs


input_dir = os.path.abspath(input_dir)
output_dir = os.path.abspath(output_dir)

os.chdir(input_dir)
if not os.path.isdir(output_dir):
  os.makedirs(output_dir)

def remove_title_empty_path(input_dir, output_dir):
  get_title = False
  parse_g = False
  ID = None
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    print ("Reading (title)", f)
    output_file = os.path.join(output_dir, f)
    lines = []
    get_title = False
    with open(f, 'r') as fh:
      for line in fh:
        if not get_title and line.strip().startswith('<title>'):
          get_title = True
          continue

        '''m = re.match('<g class="(lbl|shape)" [^/]+>"', line.strip())
        if m:
          ttype = m.group(1)
          ID = re.search('id=".*"', line).group(0)
          parse_g = True
          continue
        if parse_g:
          if line.strip().startswith('<text'):
            line = re.sub('  <text', '<text class="lbl" %s' % ID, line)
          elif line.strip().startswith('<path'):
            line = re.sub('  <path', '<path class="shape" %s' % ID, line)
          elif line.strip() == '</g>':
            parse_g = False
            continue'''
        # remove empty path
        if not line.strip().startswith('<path d="M0,0"'):
          # it removes <path d="M0,0 L23879.6,0 L23879.6,25407.0 L0,25407.0 L0,0"/>
          # TODO CHECK
          lines.append(line)

        if line == "  <defs>\n":
          lines.append('    <marker id="arrowHEE" markerWidth="10" markerHeight="10" refX="0" refY="2" orient="auto" markerUnits="strokeWidth">')
          lines.append('      <path d="M0,0 L0,4 L4,2 Z" fill="#E59400"></path>')
          lines.append('    </marker>')
          lines.append('    <marker id="arrowHFE" markerWidth="10" markerHeight="10" refX="0" refY="2" orient="auto" markerUnits="strokeWidth">')
          lines.append('      <path d="M0,0 L0,4 L4,2 Z" fill="navy"></path>')
          lines.append('    </marker>')


    with open(output_file, 'w') as fw:
      fw.write("".join(lines))


def run_svgo(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    print ("Reading (svgo)", f)
    output_file = os.path.join(output_dir, f)
    output_file = os.path.abspath(output_file)
    f = "'" + f + "'"
    output_file = "'" + output_file + "'"
    # os.system('svgo --disable=cleanupIDs --disable=convertTransform --disable=convertPathData --indent=2 --pretty -i %s -o %s' % (f, output_file))
    os.system('svgo --disable=cleanupIDs --disable=convertTransform --indent=2 --pretty -i %s -o %s' % (f, output_file))


def run_sed(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)

  un_attributs = ['fill\-opacity="1"', \
          'stroke\-width="1"', \
          'id="ID[0-9a-zA-Z]+"', \
          'font\-style="normal"', \
          'stroke\-opacity="1"']

  re_attributs = [['stroke\-linejoin="round"', 'stroke\-linejoin="miter"'], \
          ['stroke\-linecap="round"', 'stroke\-linecap="square"']]

  
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    print ("Reading (sed)", f)
    output_file = os.path.join(output_dir, f)
    output_file = os.path.abspath(output_file)
    f = "'" + f + "'"
    output_file = "'" + output_file + "'"

    # remove br and create new output file
    os.system('sed -re \'s/_br_//g\' %s > %s' % (f, output_file))

    # remove unecessary attributs
    for attr in un_attributs:
      os.system("sed -rie 's/%s//g' %s" % (attr, output_file))

    # replace asttributs
    for attr, new_attr in re_attributs:
      os.system("sed -rie 's/%s/%s/g' %s" % (attr, new_attr, output_file))

    # remove attributs on fluxEdge and effector edge
    os.system('sed -rie \'s/fill-rule="nonzero"  stroke="none"//g\' %s' % output_file)
    os.system('sed -rie \'s/(fill-rule="evenodd" ) stroke="none"/\\1/g\' %s' % output_file)

    # remove coordinate decimal
    # os.system('sed -rie \'s/([0-9]+)\.[0-9]+/\\1/g\' %s' % output_file)
    os.system('sed -rie \'s/([1-9][0-9]*\.[0-9])[0-9]+/\\1/g\' %s' % output_file)
    os.system('sed -rie \'s/(0\.[0-9]{2})[0-9]+/\\1/g\' %s' % output_file)
    os.system('sed -rie \'s/,0\.0,0\.0,/,0,0,/g\' %s' % output_file)

    # remove duplicate line coordinate
    os.system('sed -rie \'s/([LM][-]?[0-9]+([.][0-9]+)?,[-]?[0-9]+([.][0-9]+)?) \\1{1,}/\\1/g\' %s' % output_file)
    os.system('sed -rie \'s/([LM][-]?[0-9]+([.][0-9]+)?,[-]?[0-9]+([.][0-9]+)?) \\1{1,}/\\1/g\' %s' % output_file)

    # fix opacity 0.5 => 0 and version
    os.system('sed -rie \'s/version="1"/version="1.0"/g\' %s' % output_file)
    os.system('sed -rie \'s/opacity="0"/opacity="0.5"/g\' %s' % output_file)

    os.system('sed -rie \'s/omix:compartment="Compartment[$]([^"]+)"/omix:cmpt="\\1"/g\' %s' % output_file)
    # replace class and label
    os.system('sed -rie \'s/class="Metabolite" id="Metabolite[$](m[a-z0-9]+|ENSG[0-9]+)[^$]+[$]([0-9]+)"/class="metabolite" id="\\1-\\2"/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Metabolite" id="Metabolite[$](m[a-z0-9]+|ENSG[0-9]+)[^$]+"/class="metabolite" id="\\1"/g\' %s' % output_file)

    os.system('sed -rie \'s/class="Shape" id="Shape_of_Metabolite[$](m[a-z0-9]+|ENSG[0-9]+)[^$]+[$]([0-9]+)"/class="shape" id="shape_\\1-\\2"/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Shape" id="Shape_of_Metabolite[$](m[a-z0-9]+|ENSG[0-9]+)[^$]+"/class="shape" id="shape_\\1"/g\' %s' % output_file)

    os.system('sed -rie \'s/class="Label" id="Label_of_Metabolite[$](m[a-z0-9]+|ENSG[0-9]+)[^$]+[$]([0-9]+)"/class="lbl" id="label_\\1-\\2"/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Label" id="Label_of_Metabolite[$](m[a-z0-9]+|ENSG[0-9]+)[^$]+"/class="lbl" id="label_\\1"/g\' %s' % output_file)

    os.system('sed -rie \'s/class="Reaction" id="Reaction[$](HMR_[0-9]+)"/class="reaction" id="\\1"/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Reaction" id="Reaction[$]/class="reaction" id="reaction_/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Shape" id="Shape_of_Reaction[$](HMR_[0-9]+)"/class="shape" id="shape_\\1"/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Label" id="Label_of_Reaction[$](HMR_[0-9]+)"/class="lbl" id="label_\\1"/g\' %s' % output_file)

    os.system('sed -rie \'s/class="Shape" id="Shape_of_EffectorEdge[$](m[a-z0-9]+|ENSG[0-9]+_to_HMR_[0-9]+)"/class="shape" id="shape_\\1"/g\' %s' % output_file)

    # fix reaction text size,
    os.system('sed -rie \'s/font-size="8px"/font-size="21px"/g\' %s' % output_file)

    # replace remaining capitalized string
    os.system('sed -rie \'s/class="Pathway" id="Pathway[$]/class="pathway" id="pathway_/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Label" id="Label_of_Pathway/class="lbl" id="label_pathway/g\' %s' % output_file)

    os.system('sed -rie \'s/FluxEdge[$]/flux-edge_/g\' %s' % output_file)
    os.system('sed -rie \'s/FluxEdge/flux-edge/g\' %s' % output_file)
    os.system('sed -rie \'s/EffectorEdge[$]/effector-edge_/g\' %s' % output_file)
    os.system('sed -rie \'s/EffectorEdge/effector-edge/g\' %s' % output_file)

    os.system('sed -rie \'s/Shape/shape/g\' %s' % output_file)
    os.system('sed -rie \'s/class="Label"/class="lbl"/g\' %s' % output_file)
    os.system('sed -rie \'s/Label/label/g\' %s' % output_file)

    # rewrite edges
    os.system('sed -rie \'s/id="flux-edge/id="FE/g\' %s' % output_file)
    os.system('sed -rie \'s/id="effector-edge/id="EE/g\' %s' % output_file)

    # replace multiple space and multiple '_'
    os.system('sed -rie \'s/"\s{2,}/" /g\' %s' % output_file)
    # os.system('sed -rie \'s/_{2,}/_/g\' %s' % output_file)
    # remove leading '_' and br in pathway name
    # os.system('sed -rie \'s/_{1,}["]/"/g\' %s' % output_file)

    # add shape-rendering="optimizeSpeed" ?

    # remove unecessary <g> around label and shape and <title>

  # remove . svge files
  for f in os.listdir(output_dir):
    if f.endswith('.svge'):
      os.remove(os.path.join(output_dir, f))

def clean_path_name(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)

  '''to_remove = {
    'golgi.svg': ['_in_Golgi', '_Golgi_', ' (Golgi)'],
    'lysosome.svg': ['_in_Lysosome', '_Lysosome_', ' (Lysosome)'],
    'er.svg': ['_in_ER', '_ER_', ' (ER)', '_endoplasmic_reticular', ' (endoplasmic reticular)'],
    'peroxisome.svg': ['_in_Peroxisome', '_Peroxisome_', ' (Peroxisome)', '_peroxisomal_', ' (peroxisomal)'],
    'mitochondrion.svg': ['_in_Mitochondria', '_Mitochondrial_', ' (Mitochondrial)'],
    'nucleus.svg': ['_in_Nucleus', '_Nucleus_', ' (Nucleus)'],
    'cytosol_1.svg': ['_cytosolic_', ' (cytosolic)'],
    'cytosol_2.svg': ['_cytosolic_', ' (cytosolic)'],
    'cytosol_3.svg': ['_cytosolic_', ' (cytosolic)', '_endoplasmic_reticular', ' (endoplasmic reticular)'],
    'cytosol_4.svg': ['_cytosolic_', ' (cytosolic)', '_peroxisomal_', ' (peroxisomal)'],
    'cytosol_5.svg': ['_cytosolic_', ' (cytosolic)'],
    'cytosol_6.svg': ['_cytosolic_', ' (cytosolic)']
  }'''

  to_remove = {
    'golgi.svg': [' (Golgi)'],
    'lysosome.svg': [' (Lysosome)'],
    'er.svg': [' (endoplasmic reticular)', ' (ER)'],
    'peroxisome.svg': [' (Peroxisome)', ' (peroxisomal)'],
    'mitochondrion.svg': [' (Mitochondrial)'],
    'nucleus.svg': [' (Nucleus)'],
    'cytosol_1.svg': [' (cytosolic)'],
    'cytosol_2.svg': [' (cytosolic)'],
    'cytosol_3.svg': [' (cytosolic)', ' (endoplasmic reticular)'],
    'cytosol_4.svg': [' (cytosolic)', ' (peroxisomal)'],
    'cytosol_5.svg': [' (cytosolic)'],
    'cytosol_6.svg': [' (cytosolic)']
  }

  fix_sub_name = {
    'peroxisome.svg': [
        ['Beta_oxidation_of_di_unsaturated_fatty_acids__n_6_', 'Beta_oxidation_of_di_unsaturated_fatty_acids__n_6__peroxisomal_'],
        ['Beta_oxidation_of_unsaturated_fatty_acids__n_9_', 'Beta_oxidation_of_unsaturated_fatty_acids__n_9__peroxisomal_'],
        ['Beta_oxidation_of_even_chain_fatty_acids', 'Beta_oxidation_of_even_chain_fatty_acids_peroxisomal_'],
        ['Beta_oxidation_of_odd_chain_fatty_acids', 'Beta_oxidation_of_odd_chain_fatty_acids_peroxisomal_'],
      ],
      'mitochondrion.svg': [
        ['pathway_Beta_oxidation_of_even_chain___fatty_acids', 'pathway_Beta_oxidation_of_even_chain_fatty_acids'],
        ['Beta_oxidation_of_even_chain_fatty_acids', 'Beta_oxidation_of_even_chain_fatty_acids_mitochondrial_'],
        ['Beta_oxidation_of_odd_chain_fatty_acids', 'Beta_oxidation_of_odd_chain_fatty_acids_mitochondrial_'],
        ['Beta_oxidation_of_unsaturated_fatty_acids__n_9_', 'Beta_oxidation_of_unsaturated_fatty_acids__n_9__mitochondrial_'],
        ['Beta_oxidation_of_di_unsaturated_fatty_acids__n_6_', 'Beta_oxidation_of_di_unsaturated_fatty_acids__n_6__mitochondrial_'],
        ['Phenylalanine__tyrosine___and_tryptophan_biosynthesis', 'Phenylalanine__tyrosine_and_tryptophan_biosynthesis'],
        ['Terpenoid_backbone___biosynthesis', 'Terpenoid_backbone_biosynthesis'],
        ['Tricarboxylic_acid_cycle___and_glyoxylate_dicarboxylate_metabolism', 'Tricarboxylic_acid_cycle_and_glyoxylate_dicarboxylate_metabolism'],
        ['Fatty_acid_biosynthesis____even_chain', 'Fatty_acid_biosynthesis__even_chain'],
        ['Carnitine_shuttle', 'Carnitine_shuttle_mitochondrial_'],
      ],
      'lysosome.svg': [
        ['Glycosphingolipid___biosynthesis_globo_series', 'Glycosphingolipid_biosynthesis_globo_series'],
        ['Amino_sugar_and___nucleotide_sugar_metabolism', 'Amino_sugar_and_nucleotide_sugar_metabolism'],
      ],
      'er.svg': [
        ['__ER_', '__endoplasmic_reticular_'],
        ['Amino_sugar_and___nucleotide_sugar_metabolism', 'Amino_sugar_and_nucleotide_sugar_metabolism'],
        ['N_glycan_____metabolism', 'N_glycan_metabolism'],
      ],
      'golgi.svg': [
        ['Galactose____metabolism', 'Galactose_metabolism'],
        ['Nucleotide____metabolism', 'Nucleotide_metabolism'],
        ['Inositol____phosphate____metabolism', 'Inositol_phosphate_metabolism'],
        ['Sphingolipid____metabolism', 'Sphingolipid_metabolism'],
        ['Amino_sugar_____and_nucleotide____sugar_metabolism', 'Amino_sugar_and_nucleotide_sugar_metabolism'],
        ['Glycerophospholipid____metabolism', 'Glycerophospholipid_metabolism'],
        ['Glycosphingolipid____metabolism', 'Glycosphingolipid_metabolism'],
        ['Chondroitin___heparan____sulfate_biosynthesis', 'Chondroitin_heparan_sulfate_biosynthesis'],
        ['Transport__Golgi____to_lysosome', 'Transport__Golgi_to_lysosome']
      ],
      'nucleus.svg': [
        ['Nucleotide___metabolism', 'Nucleotide_metabolism'],
        ['Nicotinate_and____nicotinamide___metabolism', 'Nicotinate_and_nicotinamide_metabolism']
      ]
  }

  os.chdir(input_dir)
  for file in glob.glob("*.svg"):
    print ("Reading (_)", file)
    output_file = os.path.join(output_dir, file)
    output_file = os.path.abspath(output_file)

    if file not in to_remove and file not in fix_sub_name:
      shutil.copy(file, output_file)
    else:
      if file in to_remove:
        search_terms = to_remove[file]
        with open(file, 'r') as fh, open(output_file, 'w') as fw:
          for line in fh:
            for sterm in search_terms:
              # CHECK CHANGED Transport__ by Transport_ 29/01
              if "Transport_" not in line and sterm in line:
                line = line.replace(sterm, '')
            fw.write(line)

      if file in fix_sub_name:
        list_replace = fix_sub_name[file]
        with open(file, 'r') as fh, open(output_file, 'w') as fw:
          for line in fh:
            if line.startswith('    <g class="pathway" id=') or line.startswith('      <g class="lbl" id="'):
              for tr, nr in list_replace:
                line = line.replace(tr, nr)
            fw.write(line)


#################################################################################################################

def find_best_line(coords, expect_big_move, move_threshold=10):
    # print "-----"
    px = 0; py = 0
    dx = 0; dy = 0
    dxt = 0; dyt = 0
    big_move = 0
    big_move_incr = False
    start_x_nc = 0
    start_y_nc = 0
    for i, el in enumerate(coords):
        # print el
        # print "i ==========", i
        x, y = el.split(',')
        x = float(x[1:])
        y = float(y)
        if i == 0:
            start_x_nc = x
            start_y_nc = y
        if px and py:
            dx = x - px
            dy = y - py
            # print "dx", dx, dy
            # print "dxt", dxt, dyt
            if abs(dx) > move_threshold or abs(dy) > move_threshold:
                big_move += 1
                if big_move == expect_big_move/2:
                    # print "middle big move"
                    end_x_nc = x
                    end_y_nc = y
                elif big_move == expect_big_move/2 + 1:
                    end_x_c = end_x_nc + dxt/2
                    end_y_c = end_y_nc + dyt/2
                elif big_move == expect_big_move:
                    start_x_c = x
                    start_y_c = y
                elif big_move > expect_big_move:
                    # print "error more big move detected"
                    return None, None, None, None
                dxt = 0
                dyt = 0
            else:
                dxt += x - px
                dyt += y - py

        px = x
        py = y

    start_x_c = start_x_nc - dxt/2
    start_y_c = start_y_nc - dyt/2

    '''print "start_x_nc", start_x_nc
    print "start_y_nc", start_y_nc
    print "end_x_nc", end_x_nc
    print "end_y_nc", end_y_nc

    print "start_x_c", start_x_c
    print "start_y_c", start_y_c
    print "end_x_c", end_x_c
    print "end_y_c", end_y_c'''

    try:
        start_x_c, start_y_c, end_x_c, end_y_c
    except:
        return None, None, None, None

    return start_x_c, start_y_c, end_x_c, end_y_c

def parse_single_arrow(path_coord):
    m = re.search(' d="(M[-]?[0-9]+(?:[.][0-9]+)?,[-]?[0-9]+(?:[.][0-9]+)? (?:L[-]?[0-9]+(?:[.][0-9]+)?,[-]?[0-9]+(?:[.][0-9]+)?\s*){2,})"', path_coord)
    if not m:
        print ("error invalid path string, expected single M")
        print (path_coord)
        exit()

    return find_best_line(m.groups(0)[0].split(), 2)

def parse_double_arrow(path_coord):
    # print "path_coord", path_coord
    m = re.search(' d="(M[-]?[0-9]+(?:[.][0-9]+)?,[-]?[0-9]+(?:[.][0-9]+)? (?:L[-]?[0-9]+(?:[.][0-9]+)?,[-]?[0-9]+(?:[.][0-9]+)?\s*){2,}) (M[^"M]+)"', path_coord)
    if not m:
        print ("error invalid path string, expected a starting M")
        print (path_coord)
        exit()

    # print "m.groups(1)", m.groups(0)[0]
    # print "m.groups(2)", m.groups(0)[1]
    start1_x_c, start1_y_c, end1_x_c, end1_y_c = find_best_line(m.groups(0)[0].split(), 2, move_threshold=5)
    # print start1_x_c, start1_y_c, end1_x_c, end1_y_c

    start2_x_c, start2_y_c, end2_x_c, end2_y_c = find_best_line(m.groups(0)[1].split(), 2, )
    # print start2_x_c, start2_y_c, end2_x_c, end2_y_c
    return start1_x_c, start1_y_c, end1_x_c, end1_y_c, start2_x_c, start2_y_c, end2_x_c, end2_y_c

def reformat_EE(line):
    # get d=
    d_value = re.search(' d="([^"]+)"', line).group(1)
    c = d_value.count('M')
    if c == 1:
        start_x_c, start_y_c, end_x_c, end_y_c = parse_single_arrow(line)
        d = ' d="M%s,%s L%s,%s"' % (start_x_c, start_y_c, end_x_c, end_y_c)
        line = re.sub(' d="[^"]+"', d, line)
        line = line.replace('fill="#ffee8d"', 'stroke="#E59400" marker-end="url(#arrowHEE)"')
        line = line.replace('vector-effect="non-scaling-stroke"', 'stroke-width="2.5"')
    return line

def reformat_FE(line):
    # get d=
    d_value = re.search(' d="([^"]+)"', line).group(1)
    c = d_value.count('M')
    # print "c =", c
    if c == 1:
        start_x_c, start_y_c, end_x_c, end_y_c = parse_single_arrow(line)
        d = ' d="M%s,%s L%s,%s"' % (start_x_c, start_y_c, end_x_c, end_y_c)
        line = re.sub(' d="[^"]+"', d, line)
        line = line.replace('fill="navy"', 'stroke="navy" marker-end="url(#arrowHFE)"')
        line = line.replace('vector-effect="non-scaling-stroke"', 'stroke-width="2.5"')
    elif c == 2:
        start1_x_c, start1_y_c, end1_x_c, end1_y_c, start2_x_c, start2_y_c, end2_x_c, end2_y_c = parse_double_arrow(line)
        if not start1_x_c or not start2_x_c:
            return line
        d = ' d="M%s,%s L%s,%s M%s,%s L%s,%s"' % (start1_x_c, start1_y_c, end1_x_c, end1_y_c, start2_x_c, start2_y_c, end2_x_c, end2_y_c)
        line = re.sub(' d="[^"]+"', d, line)
        line = line.replace('fill="navy"', 'stroke="navy" marker-end="url(#arrowHFE)"')
        line = line.replace('vector-effect="non-scaling-stroke"', 'stroke-width="2.5"')
    return line


def reformat_shapes(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)

  f = sys.argv[1]
  output_file = sys.argv[2]

  os.chdir(input_dir)
  for file in glob.glob("*.svg"):
    print ("Reading (reformat shape)", file)
    output_file = os.path.join(output_dir, file)
    output_file = os.path.abspath(output_file)

    with open(file, 'r') as fh, open(output_file, 'w') as fw:
        parse_EE = False
        parse_FE = False
        for line in fh:
            line = line.strip("\n")
            if line == '    </g>':
                parse_EE = False
                fw.write(line+'\n')
                continue
            if line.startswith('    <g class="effector-edge'):
                parse_EE = True
            if parse_EE and line.startswith('      <path '):
                line = reformat_EE(line)
                parse_EE = False
            if line.startswith('    <g class="flux-edge'):
                parse_FE = True
            if parse_FE and line.startswith('      <path ') and \
                not line.startswith('      <path d="M3.2,-4'):
                line = reformat_FE(line)
                parse_FE = False
            fw.write(line+'\n')

    output_file = "'" + output_file + "'"
    # Z to reaction
    os.system('sed -rie \'s/d="M0,-25 L25,0 L0,25 L-25,0 L0,-25"/d="M0,-25 L25,0 L0,25 L-25,0 Z"/g\' %s' % output_file)

    # replace metabolite path by
    os.system(('sed -rie \'s/d="M30,0 C30,11 [^"]+"/d="M30,0 C30,25 -30,25 -30,0 C-30,-25 30,-25 30,0"/g\' %s' % output_file))

    # replace metabolite circle
    os.system(('sed -rie \'s/d="M5,0 C5,2 2,5 0,5 [^"]+"/d="M5,0 C5,6.5 -5,6.5 -5,0 C-5,-6.5 5,-6.5 5,0"/g\' %s' % output_file))

    # replace flux-edges inner arrows path by
    os.system(('sed -rie \'s/d="M3.2,-4 C3.7,-3.2 [^"]+"/d="M4,-4 L9,-1 H-8 H9 M-3,4 L-7,1 H9 H-7" stroke-width="1"/g\' %s' % output_file))
    os.system(('sed -rie \'s/(d="M4,-4 L9[^"]+" [^>]+) vector-effect="non-scaling-stroke">/\\1>/g\' %s' % output_file))

    # replace '2' path by text
    os.system(('sed -rie \'s/<path d="M0.89,-2.0 [^"]+" [^>]+ (transform="matrix[(].*[)]") [^<]+><\\/path>\
    /<text fill="#000" \\1>2<\\/text>/g\' %s' % output_file))

  # remove . svge files
  for f in os.listdir(output_dir):
    if f.endswith('.svge'):
      os.remove(os.path.join(output_dir, f))

#################################################################################################################



if __name__ == "__main__":
  # step 1
  output_dir = os.path.abspath(output_dir)
  step1_dir = os.path.join(output_dir, "STEP1")
  step2_dir = os.path.join(output_dir, "STEP2")
  step3_dir = os.path.join(output_dir, "STEP3")
  step4_dir = os.path.join(output_dir, "STEP4")
  final_dir = os.path.join(output_dir, "FINAL")

  if not os.path.isdir(step1_dir):
    os.makedirs(step1_dir)

  if not skip_rm_title:
    remove_title_empty_path(input_dir, step1_dir)
  else:
    step1_dir = input_dir

  if not os.path.isdir(step2_dir):
    os.makedirs(step2_dir)

  if not skip_sed:
    run_sed(step1_dir, step2_dir)
  else:
    step2_dir = step1_dir

  if not os.path.isdir(step3_dir):
    os.makedirs(step3_dir)

  if not skip_clean_path:
    clean_path_name(step2_dir, step3_dir)
  else:
    step3_dir = step2_dir


  if not os.path.isdir(step4_dir):
    os.makedirs(step4_dir)

  if not skip_rs:
    reformat_shapes(step3_dir, step4_dir)
  else:
    step4_dir = step3_dir

  if not skip_svgo:
    if not os.path.isdir(final_dir):
      os.makedirs(final_dir)
    run_svgo(step4_dir, final_dir)


  # print "Testing output files"
  # os.chdir(output_dir)
  # for file in glob.glob("*.svg"):
  #   with open(file, 'r') as fh:
  #     for line in fh:
  #       if re.search('_in_', line):
  #         print line
  #         exit()


# 'fill-rule="nonzero"' not for path
# 'stroke="none"' not for path


