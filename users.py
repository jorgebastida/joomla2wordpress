# -*- coding: utf-8 -*-
import MySQLdb
from databases import *
from config import *

#http://codex.wordpress.org/User_Levels
JOOMLA_PRIVILEGES_DICT = {'Super Administrator': 10,
                          'Author': 1 }
                         
def migrate_users():
    print '-'*40
    print 'Users'
    print '-'*40
    
    wp_conn = get_wordpress_connection()
    joom_conn = get_joomla_connection()
    
    wp_cursor = wp_conn.cursor()
    joom_cursor = joom_conn.cursor()
    
    general_data = {'table':'%susers' % JOOMLA_PREFIX}
    
    print 'Reading Joomla Users...',
    joom_cursor.execute ("SELECT name,username,email,password,usertype,id FROM %s" % general_data['table'])
    result_set = joom_cursor.fetchall()
    print 'OK'
    print 'Create new users:'
    
    users_list = []
    
    general_data = {'table':'%susers' % WORDPRESS_PREFIX}
    
    for row in result_set:
        
        print '\tCreating user %s...' % row[1] ,
        
        data = {'real_name':row[0],
                'username':row[1],
                'email':row[2],
                'password':row[3],
                'user_type':row[4],
                'id':row[5]}
              
        data.update(general_data)
        
        query = """
        INSERT INTO %(table)s (user_login, user_pass, user_nicename, user_email, display_name, user_status) 
        VALUES ('%(username)s', '%(password)s', '%(real_name)s', '%(email)s', '%(real_name)s', 0)"""
        
        #Insert new WP user
        result = wp_cursor.execute(query % data)
        
        if result != 1:
            raise Exception("User::Create User Error")
        
        #Get last_user_id
        wp_cursor.execute("SELECT id FROM %(table)s ORDER BY ID DESC" % general_data)
        ID = wp_cursor.fetchall()[0][0]
        
        #Add user privileges (old way prior 2.0)
        query = """INSERT INTO %(table)s (user_id, meta_key, meta_value)
        VALUES ('%(user_id)s', '%(meta_key)s', '%(meta_value)s')"""
        
        user_level = JOOMLA_PRIVILEGES_DICT.get(data['user_type'],'1')
        priv_data = {'table':'%susermeta' % WORDPRESS_PREFIX,
                     'user_id':ID,
                     'meta_key':'wp_user_level',
                     'meta_value':user_level}
        
        result = wp_cursor.execute(query % priv_data)
        if result != 1:
            raise Exception("User::Old Meta Error")
        
        #Add user privileges (new way)
        if user_level == 1:
            priv_data = {'table':'%susermeta' % WORDPRESS_PREFIX,
                        'user_id':ID,
                        'meta_key':'wp_capabilities',
                        'meta_value':'a:1:{s:6:"author";s:1:"1";}'}
        else:
            priv_data = {'table':'%susermeta' % WORDPRESS_PREFIX,
                        'user_id':ID,
                        'meta_key':'wp_capabilities',
                        'meta_value':'a:1:{s:13:"administrator";s:1:"1";}'}
                        
        result = wp_cursor.execute(query % priv_data)
        if result != 1:
            raise Exception("User::New Meta Error")
        
        #Customize Dashboard
        if user_level != 10:
            customization = [{'key':'closedpostboxes_dashboard','value':'a:0:{}'},
                            {'key':'metaboxhidden_dashboard','value':'a:6:{i:0;s:19:"dashboard_right_now";i:1;s:24:"dashboard_incoming_links";i:2;s:21:"dashboard_quick_press";i:3;s:17:"dashboard_primary";i:4;s:19:"dashboard_secondary";i:5;s:25:"dashboard_recent_comments";}'},
                            {'key':'meta-box-order_dashboard','value':'a:4:{s:6:"normal";s:154:"dashboard_right_now,dashboard_incoming_links,dashboard_quick_press,dashboard_primary,dashboard_secondary,dashboard_recent_comments,dashboard_recent_drafts";s:4:"side";s:0:"";s:7:"column3";s:0:"";s:7:"column4";s:0:"";}'},
                            {'key':'screen_layout_dashboard','value':'1'}]
        else:
            customization = [{'key':'closedpostboxes_dashboard','value':'a:0:{}'},
                            {'key':'metaboxhidden_dashboard','value':'a:6:{i:0;s:17:"dashboard_plugins";i:1;s:24:"dashboard_incoming_links";i:2;s:21:"dashboard_quick_press";i:3;s:17:"dashboard_primary";i:4;s:19:"dashboard_secondary";i:5;s:23:"dashboard_recent_drafts";}'},
                            {'key':'meta-box-order_dashboard','value':'a:4:{s:6:"normal";s:122:"dashboard_plugins,dashboard_right_now,dashboard_incoming_links,dashboard_quick_press,dashboard_primary,dashboard_secondary";s:4:"side";s:49:"dashboard_recent_drafts,dashboard_recent_comments";s:7:"column3";s:0:"";s:7:"column4";s:0:"";}'},
                            {'key':'screen_layout_dashboard','value':'2'}]
        
        for c in customization:
            priv_data = {'table':'%susermeta' % WORDPRESS_PREFIX,
                        'user_id':ID,
                        'meta_key':c['key'],
                        'meta_value':c['value']}
            result = wp_cursor.execute(query % priv_data)
        
        wp_cursor.execute("SELECT ID FROM %(table)s ORDER BY ID DESC LIMIT 1" % data)
        wp_user_id = wp_cursor.fetchall()[0][0]
            
        user = {'wp_id':wp_user_id,'joomla_id':data['id']}
        users_list.append(user)
        print 'OK'
    
    wp_cursor.close()
    joom_cursor.close()
    wp_conn.close()
    joom_conn.close()
    return users_list