# -*- coding: utf-8 -*
import os
import time

from dbfread import DBF
from pandas import concat
from simpledbf import Dbf5

import config
from lib.log import Log
from lib.map_dict import map_dict
from lib.req import Req
from lib.retry import retry


class Read():
    def __init__(self):
        pass

    def read_dbf(self, path):
        pass