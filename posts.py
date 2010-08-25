# -*- coding: utf-8 -*-
import MySQLdb
from databases import *
from config import *
from utils import slugify

def migrate_posts(users_list, categories_list):
    print '-'*40
    print 'Posts'
    print '-'*40
    
    print "Connecting... ",
    wp_conn = get_wordpress_connection()
    joom_conn = get_joomla_connection()
    
    wp_cursor = wp_conn.cursor()
    joom_cursor = joom_conn.cursor()
    
    print 'OK'
    
    general_data = {'table':'%scontent' % JOOMLA_PREFIX}
    
    print 'Reading Joomla Content... (This will take a minute)',
    joom_cursor.execute ("SELECT title, `fulltext`, introtext, state, sectionid, catid, created, created_by, metakey FROM %s" % general_data['table'])
    print 'OK'
    
    print 'Create new Posts:'
    
    general_data = {'table':'%sposts' % WORDPRESS_PREFIX}
    
    while (1):
        row = joom_cursor.fetchone()
        if row == None:
            break
        
        print '\tCreating post %s... ' % row[0],
        
        #Search author
        post_author = 0
        for user in users_list:
            if user['joomla_id'] == long(row[7]):
                post_author =  user['wp_id']
                break
        if post_author == 0:
            raise Exception("Post::User not Found Error")
                
        if str(row[3]) == '1':
            post_status = 'publish'
        else:
            post_status = 'draft'
            
        data = {'table': '%sposts' % WORDPRESS_PREFIX,
                'post_author':post_author,
                'post_date':row[6],
                'post_content':row[1].decode('iso-8859-1'),
                'post_title':row[0].decode('iso-8859-1'),
                'post_name':slugify(row[0].decode('iso-8859-1')),
                'post_status':post_status,
                'guid':'guid'
                }
                
        query = """
        INSERT INTO %(table)s (post_name, post_author, post_date, post_date_gmt, post_content, to_ping, pinged, post_content_filtered, post_excerpt, post_title, post_status, comment_status, ping_status, post_modified, post_modified_gmt, post_parent, menu_order, post_type, guid) 
        VALUES ('%(post_name)s','%(post_author)s', '%(post_date)s', '%(post_date)s','%(post_content)s', '', '', '', '', '%(post_title)s','%(post_status)s','open','open','%(post_date)s','%(post_date)s','0','0','post','%(post_date)s')"""
        
        #Insert new Post
        result = wp_cursor.execute(query % data)
        
        
        #Search category
        post_category = 0
        for category in categories_list:
            if category['joomla_id'] == long(row[5]):
                post_category =  category['wp_id']
                break
                
        if post_category != 0:
            #Get post_id
            wp_cursor.execute("SELECT ID FROM %(table)s ORDER BY ID DESC LIMIT 1" % data)
            post_id = wp_cursor.fetchall()[0][0]
        
            data = {'table':'%sterm_relationships' % WORDPRESS_PREFIX,
                    'term_taxonomy':post_category,
                    'object_id':post_id
                    }
            #Add category
            query = """
            INSERT INTO %(table)s (object_id, term_taxonomy_id, term_order) 
            VALUES ('%(object_id)s', '%(term_taxonomy)s', '0')"""
        
            wp_cursor.execute(query % data)
            
            #Increase term_taxonomy count ++
            
            data = {'table':'%sterm_taxonomy' % WORDPRESS_PREFIX,
                    'term_taxonomy_id':post_category,
                    }
            wp_cursor.execute("SELECT count FROM %(table)s WHERE term_taxonomy_id=%(term_taxonomy_id)s" % data)
            count = int(wp_cursor.fetchall()[0][0]) + 1
            
            data.update({'count':count})
            query = """
            UPDATE %(table)s SET count=%(count)s
            WHERE term_taxonomy_id='%(term_taxonomy_id)s'"""
        
            wp_cursor.execute(query % data)
            
            
        print 'OK'
    
    print 'Disconnecting... ',
    wp_cursor.close()
    joom_cursor.close()
    wp_conn.close()
    joom_conn.close()
    print 'OK'