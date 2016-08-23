import MySQLdb

f = open('config.ini')
config = {}
for line in f:
    var, val = line.strip().split('=', 1)
    config[var] = val

db = MySQLdb.connect(db=config['db'], host=config['host'],
                     port=3306, user=config['user'], passwd=config['passwd'],
                     cursorclass=DictCursor)
cur = db.cursor()

ordinal = 0
rows = []
with open('popular-ngrams') as f:
    for line in f:
        word, freq = line.strip().split('\t')
        rows.append((ordinal, word, freq))
        ordinal += 1
        if ordinal % 20000 == 0:
            cur.executemany("insert into ngram (ordinal, ngram, frequency) values (%s, %s, %s)", rows)
            rows = []
            db.commit()
            print "DONE: ", ordinal

cur.executemany("insert into ngram (ordinal, ngram, frequency) values (%s, %s, %s)", rows)
db.commit()
