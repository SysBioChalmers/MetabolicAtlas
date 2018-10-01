import sys
import os

#os.system('sed i.bak \'s/    - name:(.*)/    - name:"\\1"/g\' %s' % sys.argv[1])
os.system('sed -re \'s/    - name:\s*([^"]+)/    - name: "\\1"/g\' %s > %s.tmp && mv %s.tmp %s' % (sys.argv[1], sys.argv[1], sys.argv[1], sys.argv[1]))
#sed -e 'script script' index.html > index.html.tmp && mv index.html.tmp index.html
