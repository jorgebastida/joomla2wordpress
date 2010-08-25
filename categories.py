# -*- coding: utf-8 -*-
import MySQLdb
from databases import *
from config import *
from utils import slugify
                         
def migrate_categories():
    print '-'*40
    print 'Categories'
    print '-'*40
    
    wp_conn = get_wordpress_connection()
    joom_conn = get_joomla_connection()
    
    wp_cursor = wp_conn.cursor()
    joom_cursor = joom_conn.cursor()
    
    categories_list = []
    general_data = {'table':'%scategories' % JOOMLA_PREFIX}
    
    print 'Reading Joomla Categories...',
    joom_cursor.execute ("SELECT id, name FROM %s" % general_data['table'])
    result_set = joom_cursor.fetchall()
    print 'OK'
    
    print 'Create new categories:'
    
    for row in result_set:
        
        print '\tCreating category %s...' % row[1] ,
        
        data = {'id':row[0],
                'name':row[1].decode('iso-8859-1'),
                'slug':slugify(row[1].decode('iso-8859-1')),
                'table':u'%sterms' % WORDPRESS_PREFIX
                }
                
        query = """
        INSERT INTO %(table)s (name, slug, term_group) 
        VALUES ('%(name)s', '%(slug)s', '0')""" % data
        
        try:
            result = wp_cursor.execute(query)
        
            if result != 1:
                raise Exception("Category::Create Term Error")
            
            #Get term_id
            wp_cursor.execute("SELECT term_id FROM %(table)s ORDER BY term_id DESC LIMIT 1" % data)
            term_id = wp_cursor.fetchall()[0][0]
        
        except Exception, e: #Term already exist
            wp_cursor.execute("SELECT term_id FROM %(table)s WHERE name='%(name)s'" % data)
            term_id = wp_cursor.fetchall()[0][0]
        
        data.update({'term_id':term_id, 'table':'%sterm_taxonomy' % WORDPRESS_PREFIX})
        
        #Create term_taxonomy
        query = """
        INSERT INTO %(table)s (term_id, taxonomy, parent,description) 
        VALUES ('%(term_id)s', 'category', '0','')"""
        
        #Insert new WP term_taxonomy
        try:
            result = wp_cursor.execute(query % data)
        
            if result != 1:
                raise Exception("Category::Create Term Taxonomy Error")
            
            #Get term_taxonomy_id
            wp_cursor.execute("SELECT term_taxonomy_id FROM %(table)s ORDER BY term_taxonomy_id DESC LIMIT 1" % data)
            term_taxonomy_id = wp_cursor.fetchall()[0][0]
            
        except:#term_taxonomy already exist
            wp_cursor.execute("SELECT term_taxonomy_id FROM %(table)s WHERE term_id=%(term_id)s AND taxonomy='category' AND parent='0'" % data)
            term_taxonomy_id = wp_cursor.fetchall()[0][0]
        
        #Save term_taxonomy_id
        category = {'wp_id':term_taxonomy_id, 'joomla_id':data['id']}
        categories_list.append(category)
        
        print 'OK'
           
    wp_cursor.close()
    joom_cursor.close()
    wp_conn.close()
    joom_conn.close()
    
    return categories_list