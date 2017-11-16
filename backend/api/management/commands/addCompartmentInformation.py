###########################################################
### Go through all pathways and figure out X,Y for them ###
###########################################################
import csv
import os

from django.db import models
from api.models import *

from django.core.management.base import BaseCommand
from django.db import connection


def readCompInfo(ci_file):
    """ Read the Compartment Information base data from file """
    ciToAdd = []
    with open(ci_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for ci in reader:
            c = Compartment.objects.filter(name=ci[0])
            if not c:
                print("Cant match the compartment information name "+ci[0]+" to a compartment...")
                exit(1)
            else:
                info = CompartmentInformation(display_name=ci[1], filename=ci[2], compartment=c[0])
                ciToAdd.append(info)
    CompartmentInformation.objects.bulk_create(ciToAdd)



class Command(BaseCommand):
    ci_file = os.path.join("/project/database_generation/data/", 'compartmentInfo.tab')

    def handle(self, *args, **options):
        readCompInfo(self.ci_file)
