import urllib.request, urllib.error, urllib.parse
import os
import shelve
import sys


# The Alexa Top 1M (s3.amazonaws.com/alexa-static/top-1m.csv.zip) was retired in
# 2022 and the old address serves a placeholder now; the NetAPI Top 1M has the
# same rank,domain layout plus one header line (https://netapi.com/top-1-mln-websites/)
TOP1M_URL = 'https://netapi.com/netapi_top1mln.csv'
TOP1M_FILE = 'top-1m.csv'

if __name__ == '__main__':
    if not os.path.exists(TOP1M_FILE):
        resp = urllib.request.urlopen(TOP1M_URL)
        with open(TOP1M_FILE, 'wb') as f:
            f.write(resp.read())

    s = shelve.open('data.shelve')

    # This is a "resume" feature
    last = len(s)
    print('c(%s)' % last, end=' ')

    with open(TOP1M_FILE) as top1m:
        next(top1m)  # header line: NetAPI_Rank,Domain

        for i, line in enumerate(top1m):
            if i <= last:
                continue

            line = line.strip()
            _, domain = line.split(',')

            try:
                ok = urllib.request.urlopen('http://%s/' % domain).read()
                try:
                    bad = urllib.request.urlopen('http://%s/not-ex1st.html' % domain).read()
                except urllib.error.HTTPError as error:
                    bad = error.read()
            except KeyboardInterrupt:
                break
            except urllib.error.HTTPError:
                sys.stdout.write('4')
                sys.stdout.flush()
            except Exception:
                sys.stdout.write('E')
                sys.stdout.flush()
            else:
                s[domain] = (ok, bad)
                sys.stdout.write('.')
                sys.stdout.flush()

        sys.stdout.write('\n')
        s.close()
