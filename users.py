import MySQLdb
from databases import *

def migrate_users():
    wp_conn = get_wordpress_connection()
    joom_conn = get_joomla_connection()
    
    wp_cursor = wp_conn.cursor()
    joom_cursor = joom_conn.cursor()
    
    
    joom_cursor.execute ("SELECT * FROM jos_users")
    row = cursor.fetchone()
    for r in row:
        print r
        
        
    wp_cursor.close()
    joom_cursor.close()
    wp_conn.close()
    joom_conn.close()