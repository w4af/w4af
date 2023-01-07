Advanced tips and tricks
========================

Memory usage and caches
-----------------------

``w4af`` uses various types of caches to speed-up the scan process, one of the
most important ones is an in-memory cache which holds the result of parsing an
HTTP response body. Parsing HTTP response bodies in a CPU intensive process, and
different ``w4af`` plugins might want to parse the same response so it makes a
lot of sense to use a cache in this situation.

The `ParserCache <https://github.com/w4af/w4af/blob/main/w4af/core/data/parsers/parser_cache.py>`_
is a LRU cache which holds the items in memory to provide fast access. Some
advanced users might note that the cache size is set to a constant (10 at the
time of writing this documentation), which has these side effects:

 * ``w4af`` will consume ~250MB of RAM, most of it allocated by the cache.

 * When run on a system with low free RAM using ~250MB is good, since we want to
   avoid operating system swapping pages to disk.

 * When run on a system with 8GB of free RAM ``w4af`` could be adding more items
   to the cache and, increase the cache hit-rate, reduce the CPU usage and
   overall scan time.

Most users won't even notice all this and use ``w4af`` without this advanced
tweak, but feel free to adjust the ``CACHE_SIZE = 10`` to any value that fits
your needs.

In order to debug the cache hit-rate (which should increase with the CACHE_SIZE)
run ``w4af`` with the ``w4af_CORE_PROFILING`` environment variable set to ``1``
and inspect the JSON files at ``/tmp/w4af-*.core``