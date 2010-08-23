# -*- coding: utf-8 -*-

import MySQLdb

from config import *

def get_wordpress_connection():
    return MySQLdb.connect (host = WORDPRESS_HOST,
                            user = WORDPRESS_USER,
                            passwd = WORDPRESS_PASS,
                            db = WORDPRESS_DB)
def get_joomla_connection():
    return MySQLdb.connect (host = JOOMLA_HOST,
                            user = JOOMLA_USER,
                            passwd = JOOMLA_PASS,
                            db = JOOMLA_DB)