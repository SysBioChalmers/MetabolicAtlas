import os
import glob
import re
import sys
import shutil
import argparse
import shutil

parser = argparse.ArgumentParser(description='Short sample app')

parser.add_argument('input_dir', action="store")
parser.add_argument('output_dir', action="store")
parser.add_argument('--skip-svgo', action="store_true", default=False, dest="skip_svgo")
parser.add_argument('--skip-rm-compartment', action="store_true", default=False, dest="skip_rm_compartment")

results = parser.parse_args()
input_dir = results.input_dir
output_dir = results.output_dir
skip_svgo = results.skip_svgo
skip_rm_compartment = results.skip_rm_compartment


input_dir = os.path.abspath(input_dir)
output_dir = os.path.abspath(output_dir)

os.chdir(input_dir)
if not os.path.isdir(output_dir):
  os.makedirs(output_dir)


def remove_compartment(input_dir, output_dir):
  input_dir = os.path.abspath(input_dir)
  output_dir = os.path.abspath(output_dir)
  os.chdir(input_dir)
  for f in glob.glob("*.svg"):
    output_file = os.path.join(output_dir, f)
    output_file = os.path.abspath(output_file)
    if f == "mitochondria.svg":
      shutil.copyfile(f, output_file)
      continue
    with open(f) as fh, open(output_file, 'w') as fw:
      write = True
      for line in fh:
        if 'class="compartment"' in line:
          write = False
        elif 'class="subsystem"' in line:
          write = True
        if write:
          fw.write(line)


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


if __name__ == "__main__":
  output_dir = os.path.abspath(output_dir)
  step1_dir = os.path.join(output_dir, "STEP1")
  final_dir = os.path.join(output_dir, "FINAL")

  if not os.path.isdir(step1_dir):
    os.makedirs(step1_dir)

  if not skip_rm_compartment:
    remove_compartment(input_dir, step1_dir)
  else:
    step1_dir = input_dir

  if not skip_svgo:
    if not os.path.isdir(final_dir):
      os.makedirs(final_dir)
    run_svgo(step1_dir, final_dir)


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


