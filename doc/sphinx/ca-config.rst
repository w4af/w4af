Certificate authority configuration
===================================

All ``w4af`` proxies use the same certificate authority to intercept HTTPS
traffic. Users might find SSL certificates signed by this CA when using the
GUI's proxy tool or the ``crawl.spider_man`` plugin.

To avoid certificate errors in your browser it's recommended that you add the
CA certificate stored at ``/w4af/core/controllers/daemons/proxy/ca/`` to your
browser's list of trusted CAs.
