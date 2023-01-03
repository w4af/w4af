# Generate new CA

```python
from netlib import http_auth, certutils

ca_dir = '/home/pablo/pch/w4af/w4af/core/controllers/daemons/proxy/ca/'
certutils.CertStore.create_store(ca_dir, 'mitmproxy', o='w4af MITM CA', cn='w4af MITM CA')
```
