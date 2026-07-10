#!/bin/bash
# give table a chance to be created
sleep 20
/usr/bin/sqlite3 /juice-shop_7.5.1/data/juiceshop.sqlite "ALTER TABLE Products ADD COLUMN limitPerUser INTEGER;"
/usr/bin/sqlite3 /juice-shop_7.5.1/data/juiceshop.sqlite "ALTER TABLE Users ADD COLUMN role VARCHAR(255) DEFAULT 'customer';"
/usr/bin/sqlite3 /juice-shop_7.5.1/data/juiceshop.sqlite "UPDATE Users SET role = 'admin' WHERE id = 1;"
/usr/bin/sqlite3 /juice-shop_7.5.1/data/juiceshop.sqlite "update Products set price =RAND_INT1.99 where id=1;"
/usr/bin/sqlite3 /juice-shop_7.5.1/data/juiceshop.sqlite "update Products set price =RAND_INT2.99 where id=3;"
/usr/bin/sqlite3 /juice-shop_7.5.1/data/juiceshop.sqlite "update Products set price =RAND_INT3.99 where id=24;"
