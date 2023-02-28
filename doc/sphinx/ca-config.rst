Certificate authority configuration
===================================

All ``w4af`` proxies use the same certificate authority to intercept HTTPS
traffic. Users might find SSL certificates signed by this CA when using the
GUI's proxy tool or the ``crawl.spider_man`` plugin.

To avoid certificate errors in your browser it's recommended that you add the
CA certificate stored at ``/w4af/core/controllers/daemons/proxy/ca/`` to your
browser's list of trusted CAs.

Google Chrome
=============

To add the CA certificate to Google Chrome's CA trust for a Linux User, run
the following command:

```
certutil -d sql:$HOME/.pki/nssdb -A -t TC -n mitmproxy-ca.pem -i \
    w4af/core/controllers/daemons/proxy/ca/mitmproxy-ca.pem
```

You can confirm the certificate was added by running:

```
certutil -d sql:$HOME/.pki/nssdb/ -L
```