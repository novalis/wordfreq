This code is not very good.  That's because I banged it together in
a few hours and gave no shits.

[Try it out](http://wordfreq.novalis.org).

To run a server:

pip install bintree mysql-python pycrypto jinja2

run make.sh and wait a very long time for roughly terabytes of google
ngrams to download and process.  Make sure you have like 250 GB of
hard drive space (maybe more? I haven't even finished with the 3-grams
myself).  Oh, and you might want to edit the sort command in make.sh
if you don't have 19 gigs of RAM free.

I would recommend pypy for the make.sh step.

Edit config.ini

	dd if=/dev/urandom of=key bs=16 count=1

Run ngram-import.py
Finally, run ngram.py
