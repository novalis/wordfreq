import cgi

import os
import json

import MySQLdb
from MySQLdb.cursors import DictCursor

from Crypto.Cipher import AES
from Crypto.Hash import SHA256

from random import randint
from jinja2 import Template

with open('key') as f:
    key = f.read()

def parse_secret(secret, iv):
    obj = AES.new(key, AES.MODE_CFB, iv.decode('base64'))
    plain = obj.decrypt(secret.decode('base64'))
    j, nonce, h = plain.split("\t")
    hash = SHA256.new()
    hash.update('\t'.join((j, nonce)))
    expected = hash.hexdigest()
    assert h == expected
    ngramdata = json.loads(j)
    return ngramdata

def gen_secret(ngramdata):
    j = json.dumps(ngramdata)
    iv = os.urandom(16)
    nonce = os.urandom(16).encode('base64')
    hash = SHA256.new()
    hash.update('\t'.join((j, nonce)))
    h = hash.hexdigest()
    plain = '\t'.join((j, nonce, h))
    obj = AES.new(key, AES.MODE_CFB, iv)
    return obj.encrypt(plain).encode('base64'), iv.encode('base64')

def render_template(out):
    with open('ngram.html') as f:
        template = Template(f.read())
        encoded = {}
        for k, v in out.items():
            if isinstance(v, str):
                v = v.decode('utf-8')
            encoded[k] = v
        return template.render(**out)

def run(form):
    out = {}
    out['prev'] = False
    out['ncorrect'] = out['ntried'] = 0

    secret = form.getvalue('secret')
    if secret:
        iv = form.getvalue('iv')
        ngramdata = parse_secret(secret, iv)
        out.update(ngramdata)
        choice = form.getvalue('choice')
        if choice:
            out['correct'] = ngramdata['popularngram'] == choice
            out['prev'] = True
            if out['correct']:
                out['ncorrect'] += 1
            out['ntried'] += 1


    if out['ntried']:
        out['ratio'] = int(float(out['ncorrect']) * 100 / out['ntried'])
    max_ordinal = 2**23

    try:
        difficulty = int(form.getvalue('difficulty'))
    except:
        difficulty = 20
    out['difficulty'] = str(difficulty)

    difference = max_ordinal / (10 + difficulty)

    ordinal1 = randint(0, (max_ordinal - difference) - 1)
    ordinal2 = ordinal1 + difference

    f = open('config.ini')
    config = {}
    for line in f:
        var, val = line.strip().split('=', 1)
        config[var] = val

    db = MySQLdb.connect(db=config['db'], host=config['host'],
                         port=3306, user=config['user'], passwd=config['passwd'],
                         cursorclass=DictCursor)
    cur = db.cursor()

    cur.execute("""select ngram, frequency from ngram where
    ordinal = %s or ordinal = %s order by frequency desc""", (ordinal1,ordinal2))

    rows = list(cur.fetchall())
    if randint(0, 1) == 0:
        i1, i2 = 0, 1
    else:
        i1, i2 = 1, 0

    out['ngram1'] = rows[i1]['ngram']
    out['ngram2'] = rows[i2]['ngram']
    ngramdata = {
        'popularngram' : rows[0]['ngram'],
        'unpopularngram' : rows[1]['ngram'],
        'popularfreq' : rows[0]['frequency'],
        'unpopularfreq' : rows[1]['frequency'],
        'ncorrect' : out['ncorrect'],
        'ntried' : out['ntried'],
    }
    out['secret'], out['iv'] = gen_secret(ngramdata)

    return render_template(out)

def application(environ, start_response):
    if environ['REQUEST_METHOD'] == 'POST':
        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        form = cgi.FieldStorage(
            fp = environ['wsgi.input'],
            environ = post_env,
            keep_blank_values = True
        )
    else:
        form = cgi.FieldStorage(
            environ = environ,
            keep_blank_values = True
        )
    start_response('200 OK', [('Content-Type', 'text/html')])
    return [run(form).encode('utf-8')]


if __name__ == '__main__':
    try:
        from wsgiref.simple_server import make_server
        httpd = make_server('', 8080, application)
        print('Serving on port 8080...')
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Goodbye.')
