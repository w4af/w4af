Spider man plugin
===================================

With the ``spider_man`` plugin enabled, ``w4af`` expects you to configure
a local web-browser to use ``w4af`` as an http proxy:

```
google-chrome --proxy-server="http://127.0.0.1:44444"
```

The ``spider_man`` plugin will log all URLs fetched by the web-browser.
You can then browse the target website as you normally would, and the
configured ``grep`` and ``audit`` plugins will report their analysis of all
URLs discovered by your browsing.

As described in `Certificate Authority Configuration </ca-config>`, you will
need to add the ``w4af`` CA certificate to your browser's trust root to avoid
errors when browsing SSL websites.

To terminate the ``spider_man`` scan, you need to browse to the termination
URL (``http://127.7.7.7/spider_man?terminate``) in your proxied browser. Since
some browsers bypass the proxy server for local connections, you may need to
hit this URL with ``curl`` in order to terminate your session:

```
curl -x http://127.0.0.1:44444 http://127.7.7.7/spider_man?terminate
```