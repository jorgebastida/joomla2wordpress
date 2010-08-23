# -*- coding: utf-8 -*-
import MySQLdb
from databases import *
from config import *

#http://codex.wordpress.org/User_Levels
JOOMLA_PRIVILEGES_DICT = {'Super Administrator':123,
                     'Author': 234}
def migrate_users():
    wp_conn = get_wordpress_connection()
    joom_conn = get_joomla_connection()
    
    wp_cursor = wp_conn.cursor()
    joom_cursor = joom_conn.cursor()
    
    general_data = {'table':'%susers' % WORDPRESS_PREFIX}
    
    joom_cursor.execute ("SELECT name,username,email,password,usertype FROM jos_users")
    result_set = joom_cursor.fetchall()
    print result_set
    for row in result_set:
       data = {'real_name':row[0],
               'username':row[1],
               'email':row[2],
               'password':row[3],
               'user_type':row[4]
              }
              
       data.update(general_data)
       
       query = """
       INSERT INTO %(table)s (user_login, user_pass, user_nicename, user_email, display_name) 
       VALUES ('%(username)s', '%(password)s', '%(real_name)s', '%(email)s', '%(real_name)s')""" % data
       
       #Insert new WP user
       result = wp_cursor.execute(query)
       
       if result != 1:
           raise Exception("User Table Migration failed")
       
       #Get last_user_id
       wp_cursor.execute("SELECT id FROM %(table)s ORDER BY ID DESC" % general_data)
       ID = wp_cursor.fetchall()[0][0]
       
       #Add user privileges
       wp_level = 0
       
           
    wp_cursor.close()
    joom_cursor.close()
    wp_conn.close()
    joom_conn.close()