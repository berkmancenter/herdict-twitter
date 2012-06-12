"""
Display stories in a random order, to avoid biasing events chronologically
Add option to undo previous entry
Print database statistics on quit, too
"""


import pymongo


# Import parameters.
with open('/home/twitter-data/docs/parameters.json') as f:
    par = json.loads(f.read())


# Connect to MongoDB.
conn = pymongo.Connection(par['server_name'])
db = getattr(conn, par['database_name'])


cursor = db.statuses.find({'censorship' : {'$exists' : False}})

print '{} tweets in database'.format(db.articles.count())
print '{} judged'.format(db.articles.count() - cursor.count())
print '{} left to judge'.format(cursor.count())

print 'Press "q" to quit.'

for document in cursor:
    print '\n'.join('\n', document['user_name'], document['text'])
    censorship = raw_input('Does the tweet refer to censorship: (y, n)')
    if censorship = 'q':
        break
    while censorship not in ('y', 'n'):
        print '\nPlease enter one of (y, n).'
        censorship = raw_input('Does the tweet refer to censorship: (y, n)')
    document['censorship'] = censorship
    db.statuses.save(document)

conn.disconnect()


if __name__ == '__main__':
    
    main()


