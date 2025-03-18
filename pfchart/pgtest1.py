#!/usr/bin/python

import pg

conn = pg.DB(host="localhost", user="wls", passwd="wholelifestocks", dbname="wls")

result = conn.query("SELECT fname, lname FROM employee")

for firstname, lastname in result.getresult() :
    print firstname, lastname

conn.close()
