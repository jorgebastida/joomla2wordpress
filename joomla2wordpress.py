#!/usr/bin/python
# -*- coding: utf-8 -*-

from users import migrate_users
from posts import migrate_posts
from categories import migrate_categories
def main():
    users_list = migrate_users()
    categories_list = migrate_categories()
    migrate_posts(users_list, categories_list)

if __name__ == '__main__':
    main()