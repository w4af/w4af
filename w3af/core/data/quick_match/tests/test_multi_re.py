import unittest

from w4af.core.data.quick_match.multi_re import MultiRE

class MultiRETest(unittest.TestCase):

    VERSION_REGEX = (
        (r'<address>(.*?)</address>', 'Apache'),
        (r'<HR size="1" noshade="noshade"><h3>(.*?)</h3></body>',
         'Apache Tomcat'),
        (r'<a href="http://www.microsoft.com/ContentRedirect.asp\?prd=iis&sbp=&pver=(.*?)&pid=&ID', 'IIS'),

        # <b>Version Information:</b>&nbsp;Microsoft .NET Framework Version:1.1.4322.2300; ASP.NET Version:1.1.4322.2300
        (r'<b>Version Information:</b>&nbsp;(.*?)\n', 'ASP .NET')
    )
    _multi_re = MultiRE(VERSION_REGEX)

    def test_multi_re(self):
        for match, matching_regexp_str, compiled_regexp, regexp_name in self._multi_re.query("<html><head><address>123456</address></head></html>"):
            self.assertEqual(match[1], '123456', "expected string to match")
            self.assertEqual('<address>(.*?)</address>', matching_regexp_str)
            self.assertEqual("Apache", regexp_name)

if __name__ == '__main__':
    unittest.main()
