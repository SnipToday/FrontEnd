import json
import os
from json import encoder

from django.core.management import BaseCommand
from sympy import solve, exp, Symbol

class Command(BaseCommand):
    help = 'Upload images to wagtail cms'


    def add_arguments(self, parser):
        parser.add_argument('-max_days', default='180')

    def handle(self, *args, **options):
        a = Symbol('a')
        max_days = int(options['max_days'])
        death_factors = {}
        for d in range(1, max_days+1):
            res = solve(exp(-1 / (a * d ** a)) - 0.8)[0]
            death_factors[d] = format(res, '.5f')
        file_name = os.environ.get('DECAY_DICT_FILE')

        with open(file_name, 'w') as outfile:
            json.dump(death_factors, outfile)



