# -*- coding: utf8 -*-
"""
test_xml_file.py

Copyright 2012 Andres Riancho

This file is part of w4af, http://w4af.net/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""
import base64
import io
import os
import os.path
import pytest
import re
import unittest
import xml.etree.ElementTree as ElementTree

from lxml import etree

import w4af.core.data.constants.severity as severity
import w4af.core.data.kb.knowledge_base as kb

from w4af import ROOT_PATH

from w4af.core.controllers.w4afCore import w4afCore
from w4af.core.controllers.misc.temp_dir import create_temp_dir, remove_temp_dir
from w4af.core.controllers.ci.moth import get_moth_http
from w4af.core.data.kb.tests.test_vuln import MockVuln
from w4af.core.data.kb.vuln import Vuln
from w4af.core.data.db.history import HistoryItem
from w4af.core.data.db.url_tree import URLTree
from w4af.core.data.dc.headers import Headers
from w4af.core.data.parsers.doc.url import URL
from w4af.core.data.url.HTTPResponse import HTTPResponse
from w4af.core.data.url.HTTPRequest import HTTPRequest
from w4af.core.data.options.option_list import OptionList
from w4af.core.data.options.opt_factory import opt_factory
from w4af.core.data.options.option_types import OUTPUT_FILE
from w4af.plugins.tests.helper import PluginTest, PluginConfig, MockResponse
from w4af.plugins.output.xml_file import (xml_file, CachedXMLNode, FindingsCache,
                                          HTTPTransaction, ScanInfo, ScanStatus,
                                          Finding, jinja2_attr_value_escape_filter)


@pytest.mark.smoke
@pytest.mark.moth
class TestXMLOutput(PluginTest):

    target_url = get_moth_http('/audit/sql_injection/where_integer_qs.py')

    FILENAME = 'output-unittest.xml'
    XSD = os.path.join(ROOT_PATH, 'plugins', 'output', 'xml_file', 'report.xsd')

    _run_configs = {
        'cfg': {
            'target': target_url + '?id=3',
            'plugins': {
                'audit': (PluginConfig('sqli'),),
                'output': (
                    PluginConfig(
                        'xml_file',
                        ('output_file', FILENAME, PluginConfig.STR)),
                )
            },
        }
    }

    def test_found_vuln(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        kb_vulns = self.kb.get('sqli', 'sqli')
        file_vulns = get_vulns_from_xml(self.FILENAME)

        self.assertEqual(len(kb_vulns), 1, kb_vulns)

        self.assertEqual(
            set(sorted([v.get_url() for v in kb_vulns])),
            set(sorted([v.get_url() for v in file_vulns]))
        )

        self.assertEqual(
            set(sorted([v.get_name() for v in kb_vulns])),
            set(sorted([v.get_name() for v in file_vulns]))
        )

        self.assertEqual(
            set(sorted([v.get_plugin_name() for v in kb_vulns])),
            set(sorted([v.get_plugin_name() for v in file_vulns]))
        )

        with open(self.FILENAME, "rb") as file_h:
            self.assertEqual(validate_xml(file_h.read(), self.XSD), '')

    def tearDown(self):
        super(TestXMLOutput, self).tearDown()
        try:
            os.remove(self.FILENAME)
        except:
            pass
        finally:
            self.kb.cleanup()

    def test_error_null_byte(self):
        w4af_core = w4afCore()
        w4af_core.status.start()

        plugin_instance = xml_file()
        plugin_instance.set_w4af_core(w4af_core)

        # https://github.com/andresriancho/w4af/issues/12924
        plugin_instance.error('\0')
        plugin_instance.flush()


class TestNoDuplicate(unittest.TestCase):
    
    FILENAME = 'output-unittest.xml'
    
    def setUp(self):
        kb.kb.cleanup()
        create_temp_dir()
        CachedXMLNode.create_cache_path()
        FindingsCache.create_cache_path()
        HistoryItem().init()
        self.w4af_core = w4afCore()
        self.w4af_core.status.start()

    def tearDown(self):
        remove_temp_dir()
        HistoryItem().clear()
        kb.kb.cleanup()

    def test_no_duplicate_vuln_reports(self):
        # The xml_file plugin had a bug where vulnerabilities were written to
        # disk multiple times, this test makes sure I fixed that vulnerability

        # Write the HTTP request / response to the DB
        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>syntax error near', hdr, url, url)

        _id = 1

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        # Create one vulnerability in the KB pointing to the request-
        # response we just created
        desc = 'Just a test for the XML file output plugin.'
        v = Vuln('SQL injection', desc, severity.HIGH, _id, 'sqli')
        kb.kb.append('sqli', 'sqli', v)

        self.assertEqual(len(kb.kb.get_all_vulns()), 1)

        # Setup the plugin
        plugin_instance = xml_file()
        plugin_instance.set_w4af_core(self.w4af_core)

        # Set the output file for the unittest
        ol = OptionList()
        d = 'Output file name where to write the XML data'
        o = opt_factory('output_file', self.FILENAME, d, OUTPUT_FILE)
        ol.add(o)

        # Then we flush() twice to disk, this reproduced the issue
        plugin_instance.set_options(ol)
        plugin_instance.flush()
        plugin_instance.flush()
        plugin_instance.flush()

        # Now we parse the vulnerabilities from disk and confirm only one
        # is there
        file_vulns = get_vulns_from_xml(self.FILENAME)
        self.assertEqual(len(file_vulns), 1, file_vulns)


class XMLParser(object):

    def __init__(self):
        self.vulns = []
        self._inside_body = False
        self._inside_response = False
        self._data_parts = []
    
    def start(self, tag, attrib):
        """
        <vulnerability id="[87]" method="GET"
                       name="Cross site scripting vulnerability"
                       plugin="xss" severity="Medium"
                       url="http://moth/w4af/audit/xss/simple_xss_no_script_2.php"
                       var="text">
        """
        if tag == 'vulnerability':
            name = attrib['name']
            plugin = attrib['plugin']
            
            v = MockVuln(name, None, 'High', 1, plugin)
            v.set_url(URL(attrib['url']))
            
            self.vulns.append(v)
        
        # <body content-encoding="base64">
        elif tag == 'body':
            content_encoding = attrib['content-encoding']
            
            assert content_encoding == 'base64'
            self._inside_body = True

        elif tag == 'http-response':
            self._inside_response = True
    
    def end(self, tag):
        if tag == 'body' and self._inside_response:
            
            data = ''.join(self._data_parts)

            data_decoded = base64.b64decode(data)
            assert b'syntax error' in data_decoded, data_decoded
            assert b'near' in data_decoded, data_decoded
            
            self._inside_body = False
            self._data_parts = []

        if tag == 'http-response':
            self._inside_response = False

    def data(self, data):
        if self._inside_body and self._inside_response:
            self._data_parts.append(data)

    def close(self):
        return self.vulns


def get_vulns_from_xml(filename):
    xp = XMLParser()
    parser = etree.XMLParser(target=xp)
    with open(filename, "rb") as file_h:
        vulns = etree.fromstring(file_h.read(), parser)
    return vulns


def validate_xml(content, schema_content):
    """
    Validate an XML against an XSD.

    :return: The validation error log as a string, an empty string is returned
             when there are no errors.
    """
    xml_schema_doc = etree.parse(schema_content)
    xml_schema = etree.XMLSchema(xml_schema_doc)
    xml = etree.parse(io.BytesIO(content))

    # Validate the content against the schema.
    try:
        xml_schema.assertValid(xml)
    except etree.DocumentInvalid:
        return xml_schema.error_log

    return ''


class TestXMLOutputBinary(PluginTest):

    target_url = 'http://rpm-path-binary/'

    TEST_FILE = os.path.join(ROOT_PATH, 'plugins', 'tests', 'output',
                             'data', 'nsepa32.rpm')

    MOCK_RESPONSES = [
              MockResponse(url='http://rpm-path-binary/',
                           body=open(TEST_FILE, "rb").read(),
                           content_type='text/plain',
                           method='GET', status=200),
    ]

    FILENAME = 'output-unittest.xml'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'grep': (PluginConfig('path_disclosure'),),
                'output': (
                    PluginConfig(
                        'xml_file',
                        ('output_file', FILENAME, PluginConfig.STR)),
                )
            },
        }
    }

    def test_binary_handling_in_xml(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        self.assertEqual(len(self.kb.get_all_findings()), 1)

        try:
            tree = ElementTree.parse(self.FILENAME)
            tree.getroot()
        except Exception as e:
            self.assertTrue(False, 'Generated invalid XML: "%s"' % e)

    def tearDown(self):
        super(TestXMLOutputBinary, self).tearDown()
        try:
            os.remove(self.FILENAME)
        except:
            pass
        finally:
            self.kb.cleanup()


class TestXML0x0B(PluginTest):

    target_url = 'http://0x0b-path-binary/'

    TEST_FILE = os.path.join(ROOT_PATH, 'plugins', 'tests', 'output',
                             'data', '0x0b.html')

    MOCK_RESPONSES = [
              MockResponse(url='http://0x0b-path-binary/',
                           body=open(TEST_FILE).read(),
                           content_type='text/plain',
                           method='GET', status=200),
    ]

    FILENAME = 'output-unittest.xml'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'grep': (PluginConfig('path_disclosure'),),
                'output': (
                    PluginConfig(
                        'xml_file',
                        ('output_file', FILENAME, PluginConfig.STR)),
                )
            },
        }
    }

    def test_binary_0x0b_handling_in_xml(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        self.assertEqual(len(self.kb.get_all_findings()), 1)

        try:
            tree = ElementTree.parse(self.FILENAME)
            tree.getroot()
        except Exception as e:
            self.assertTrue(False, 'Generated invalid XML: "%s"' % e)

    def tearDown(self):
        super(TestXML0x0B, self).tearDown()
        try:
            os.remove(self.FILENAME)
        except:
            pass
        finally:
            self.kb.cleanup()


class TestSpecialCharacterInURL(PluginTest):

    target_url = 'http://hello.se/%C3%93%C3%B6'

    MOCK_RESPONSES = [
              MockResponse(url=target_url,
                           body='hi there á! /var/www/site/x.php path',
                           content_type='text/plain',
                           method='GET', status=200),
    ]

    FILENAME = 'output-unittest.xml'

    _run_configs = {
        'cfg': {
            'target': target_url,
            'plugins': {
                'grep': (PluginConfig('path_disclosure'),),
                'output': (
                    PluginConfig(
                        'xml_file',
                        ('output_file', FILENAME, PluginConfig.STR)),
                )
            },
        }
    }

    def test_special_character_in_url_handling(self):
        cfg = self._run_configs['cfg']
        self._scan(cfg['target'], cfg['plugins'])

        self.assertEqual(len(self.kb.get_all_findings()), 1)

        try:
            tree = ElementTree.parse(self.FILENAME)
            tree.getroot()
        except Exception as e:
            self.assertTrue(False, 'Generated invalid XML: "%s"' % e)

    def tearDown(self):
        super(TestSpecialCharacterInURL, self).tearDown()
        try:
            os.remove(self.FILENAME)
        except:
            pass
        finally:
            self.kb.cleanup()


class XMLNodeGeneratorTest(unittest.TestCase):
    def assertValidXML(self, xml):
        etree.fromstring(xml)
        assert 'escape_attr' not in xml


class TestHTTPTransaction(XMLNodeGeneratorTest):
    def setUp(self):
        kb.kb.cleanup()
        create_temp_dir()
        CachedXMLNode.create_cache_path()
        FindingsCache.create_cache_path()
        HistoryItem().init()

    def tearDown(self):
        remove_temp_dir()
        HistoryItem().clear()
        kb.kb.cleanup()

    def test_render_simple(self):
        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        _id = 1

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()
        http_transaction = HTTPTransaction(x._get_jinja2_env(), _id)
        xml = http_transaction.to_string()

        expected = ('<http-transaction id="1">\n\n'
                    '    <http-request>\n'
                    '        <status>POST http://w4af.com/a/b/c.php HTTP/1.1</status>\n'
                    '        <headers>\n'
                    '            <header field="User-agent" content="w4af" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">YT0x</body>\n'
                    '    </http-request>\n\n'
                    '    <http-response>\n'
                    '        <status>HTTP/1.1 200 OK</status>\n'
                    '        <headers>\n'
                    '            <header field="Content-Type" content="text/html" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">PGh0bWw+</body>\n'
                    '    </http-response>\n\n</http-transaction>')

        self.assertEqual(expected, xml)
        self.assertValidXML(xml)

    def test_cache(self):
        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        _id = 2

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()
        http_transaction = HTTPTransaction(x._get_jinja2_env(), _id)

        self.assertIsNone(http_transaction.get_node_from_cache())

        # Writes to cache
        xml = http_transaction.to_string()

        expected = ('<http-transaction id="2">\n\n'
                    '    <http-request>\n'
                    '        <status>POST http://w4af.com/a/b/c.php HTTP/1.1</status>\n'
                    '        <headers>\n'
                    '            <header field="User-agent" content="w4af" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">YT0x</body>\n'
                    '    </http-request>\n\n'
                    '    <http-response>\n'
                    '        <status>HTTP/1.1 200 OK</status>\n'
                    '        <headers>\n'
                    '            <header field="Content-Type" content="text/html" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">PGh0bWw+</body>\n'
                    '    </http-response>\n\n</http-transaction>')
        self.assertEqual(expected, xml)

        # Yup, we're cached
        self.assertIsNotNone(http_transaction.get_node_from_cache())

        # Make sure they are all the same
        cached_xml = http_transaction.get_node_from_cache()
        self.assertEqual(cached_xml, expected)

        xml = http_transaction.to_string()
        self.assertEqual(expected, xml)


class TestScanInfo(XMLNodeGeneratorTest):
    def setUp(self):
        kb.kb.cleanup()
        create_temp_dir()
        CachedXMLNode.create_cache_path()
        FindingsCache.create_cache_path()
        HistoryItem().init()

    def tearDown(self):
        remove_temp_dir()
        HistoryItem().clear()
        kb.kb.cleanup()

    def test_render_simple(self):
        w4af_core = w4afCore()

        w4af_core.plugins.set_plugins(['sqli'], 'audit')
        w4af_core.plugins.set_plugins(['web_spider'], 'crawl')

        plugin_inst = w4af_core.plugins.get_plugin_inst('crawl', 'web_spider')
        web_spider_options = plugin_inst.get_options()

        w4af_core.plugins.set_plugin_options('crawl', 'web_spider', web_spider_options)

        plugins_dict = w4af_core.plugins.get_all_enabled_plugins()
        options_dict = w4af_core.plugins.get_all_plugin_options()
        scan_target = 'https://w4af.net'

        x = xml_file()

        scan_info = ScanInfo(x._get_jinja2_env(), scan_target, plugins_dict, options_dict)
        xml = scan_info.to_string()

        expected = ('<scan-info target="https://w4af.net">\n'
                    '    <audit>\n'
                    '            <plugin name="sqli">\n'
                    '            </plugin>\n'
                    '    </audit>\n'
                    '    <grep>\n'
                    '    </grep>\n'
                    '    <bruteforce>\n'
                    '    </bruteforce>\n'
                    '    <crawl>\n'
                    '            <plugin name="web_spider">\n'
                    '                        <config parameter="only_forward" value="False"/>\n'
                    '                        <config parameter="follow_regex" value=".*"/>\n'
                    '                        <config parameter="ignore_regex" value=""/>\n'
                    '                        <config parameter="ignore_extensions" value=""/>\n'
                    '            </plugin>\n'
                    '    </crawl>\n'
                    '    <evasion>\n'
                    '    </evasion>\n'
                    '    <mangle>\n'
                    '    </mangle>\n'
                    '    <output>\n'
                    '    </output>\n'
                    '    <auth>\n'
                    '    </auth>\n'
                    '    <infrastructure>\n'
                    '    </infrastructure>\n'
                    '</scan-info>')

        self.assertEqual(xml, expected)
        self.assertValidXML(xml)

def clear_variable_tags(xml_string):
    for tag in ('rpm', 'sent-request-count'):
        tagr = re.compile(r"<%s>.*</%s>" % (tag, tag))
        xml_string = re.sub(tagr, "<%s></%s>" % (tag, tag), xml_string)
    return xml_string

class TestScanStatus(XMLNodeGeneratorTest):
    def setUp(self):
        kb.kb.cleanup()
        create_temp_dir()

    def tearDown(self):
        remove_temp_dir()
        HistoryItem().clear()
        kb.kb.cleanup()

    def test_render_simple(self):
        w4af_core = w4afCore()

        w4af_core.status.start()
        w4af_core.status.set_running_plugin('crawl', 'web_spider')
        status = w4af_core.status.get_status_as_dict()

        known_urls = URLTree()
        known_urls.add_url(URL('http://w4af.net/'))
        known_urls.add_url(URL('http://w4af.net/foo/'))
        known_urls.add_url(URL('http://w4af.net/foo/abc.html'))
        known_urls.add_url(URL('http://w4af.net/foo/bar/'))
        known_urls.add_url(URL('http://w4af.net/123.txt'))

        total_urls = 150

        x = xml_file()

        scan_status = ScanStatus(x._get_jinja2_env(), status, total_urls, known_urls)
        xml = scan_status.to_string()
        self.maxDiff = None
        expected = ('<scan-status>\n'
                    '    <status>Running</status>\n'
                    '    <is-paused>False</is-paused>\n'
                    '    <is-running>True</is-running>\n'
                    '\n'
                    '    <active-plugin>\n'
                    '        <crawl>web_spider</crawl>\n'
                    '        <audit>None</audit>\n'
                    '    </active-plugin>\n'
                    '\n'
                    '    <current-request>\n'
                    '        <crawl>None</crawl>\n'
                    '        <audit>None</audit>\n'
                    '    </current-request>\n'
                    '\n'
                    '    <queues>\n'
                    '        <crawl>\n'
                    '            <input-speed>0</input-speed>\n'
                    '            <output-speed>0</output-speed>\n'
                    '            <length>0</length>\n'
                    '            <processed-tasks>0</processed-tasks>\n'
                    '        </crawl>\n'
                    '\n'
                    '        <audit>\n'
                    '            <input-speed>0</input-speed>\n'
                    '            <output-speed>0</output-speed>\n'
                    '            <length>0</length>\n'
                    '            <processed-tasks>0</processed-tasks>\n'
                    '        </audit>\n'
                    '\n'
                    '        <grep>\n'
                    '            <input-speed>0</input-speed>\n'
                    '            <output-speed>0</output-speed>\n'
                    '            <length>0</length>\n'
                    '            <processed-tasks>None</processed-tasks>\n'
                    '        </grep>\n'
                    '    </queues>\n'
                    '\n'
                    '    <eta>\n'
                    '        <crawl>0 seconds</crawl>\n'
                    '        <audit>0 seconds</audit>\n'
                    '        <grep>0 seconds</grep>\n'
                    '        <all>0 seconds</all>\n'
                    '    </eta>\n'
                    '\n'
                    '    <rpm>0</rpm>\n'
                    '    <sent-request-count>0</sent-request-count>\n'
                    '    <progress>100</progress>\n'
                    '\n'
                    '    <total-urls>150</total-urls>\n'
                    '    <known-urls>    \n'   
                    '    <node url="http://w4af.net" exists="1">\n'
                    '                                        \n'
                    '        <node url="123.txt" exists="1" />        \n'
                    '        <node url="foo" exists="1">\n'
                    '                                            \n'
                    '            <node url="abc.html" exists="1" />                            \n'
                    '            <node url="bar" exists="1" />\n'
                    '                        \n'
                    '        </node>\n'
                    '                    \n'
                    '    </node>\n'
                    '    </known-urls>\n'
                    '</scan-status>')

        self.assertEqual(clear_variable_tags(xml), clear_variable_tags(expected))
        self.assertValidXML(xml)


class TestFinding(XMLNodeGeneratorTest):
    def setUp(self):
        kb.kb.cleanup()
        create_temp_dir()
        CachedXMLNode.create_cache_path()
        FindingsCache.create_cache_path()
        HistoryItem().init()

    def tearDown(self):
        remove_temp_dir()
        HistoryItem().clear()
        kb.kb.cleanup()

    def test_render_simple(self):
        _id = 2

        vuln = MockVuln(_id=_id)

        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()

        finding = Finding(x._get_jinja2_env(), vuln)
        xml = finding.to_string()

        expected = ('<vulnerability id="[2]" method="GET" name="TestCase" plugin="plugin_name" severity="High" url="None" var="None">\n'
                    '    <description>Foo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggs</description>\n\n\n'
                    '    <http-transactions>\n'
                    '            <http-transaction id="2">\n\n'
                    '    <http-request>\n'
                    '        <status>POST http://w4af.com/a/b/c.php HTTP/1.1</status>\n'
                    '        <headers>\n'
                    '            <header field="User-agent" content="w4af" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">YT0x</body>\n'
                    '    </http-request>\n\n'
                    '    <http-response>\n'
                    '        <status>HTTP/1.1 200 OK</status>\n'
                    '        <headers>\n'
                    '            <header field="Content-Type" content="text/html" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">PGh0bWw+</body>\n'
                    '    </http-response>\n\n'
                    '</http-transaction>\n'
                    '    </http-transactions>\n'
                    '</vulnerability>')

        self.assertEqual(xml, expected)
        self.assertValidXML(xml)

    def test_render_with_special_chars(self):
        _id = 2

        desc = ('This is a long description that contains some special'
                ' characters such as <, & and > which MUST be encoded'
                ' by jinja2.')

        vuln = MockVuln(_id=_id)
        vuln.set_desc(desc)

        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()

        finding = Finding(x._get_jinja2_env(), vuln)
        xml = finding.to_string()

        self.assertNotIn('such as <, & and > which MUST', xml)
        self.assertIn('such as &lt;, &amp; and &gt; which MUST', xml)
        self.assertValidXML(xml)

    def test_render_with_unicode_control_chars(self):
        _id = 2

        desc = ('This is a long description that contains some special'
                ' unicode control characters such as \f and \x09')

        vuln = MockVuln(_id=_id)
        vuln.set_desc(desc)

        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()

        finding = Finding(x._get_jinja2_env(), vuln)
        xml = finding.to_string()

        self.assertNotIn('unicode control characters such as \f and \x09', xml)
        self.assertIn('unicode control characters such as <character code="000c"/> and <character code="0009"/>', xml)
        self.assertValidXML(xml)

    def test_render_attr_with_special_chars(self):
        _id = 2

        name = 'A long description with special characters: <&">'

        vuln = MockVuln(_id=_id)
        vuln.set_name(name)

        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()

        finding = Finding(x._get_jinja2_env(), vuln)
        xml = finding.to_string()

        self.assertNotIn(name, xml)
        self.assertIn('A long description with special characters: &lt;&amp;&quot;&gt;', xml)
        self.assertValidXML(xml)

    def test_render_unicode_bytestring(self):
        vuln = MockVuln(name='á')
        vuln.set_id([])

        x = xml_file()

        finding = Finding(x._get_jinja2_env(), vuln)
        xml = finding.to_string()

        self.assertIn('á', xml)
        self.assertValidXML(xml)

    def test_render_url_special_chars(self):
        self.maxDiff = None

        _id = 2
        vuln = MockVuln(_id=_id)

        url = URL('https://w4af.com/._basebind/node_modules/lodash._basecreate/'
                  'LICENSE.txt\x00=ڞ')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        vuln.set_uri(url)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        x = xml_file()

        finding = Finding(x._get_jinja2_env(), vuln)
        xml = finding.to_string()

        expected = ('<vulnerability id="[2]" method="GET" name="TestCase" plugin="plugin_name" severity="High" url="https://w4af.com/._basebind/node_modules/lodash._basecreate/LICENSE.txt&lt;character code=&quot;0000&quot;/&gt;=\u069e" var="None">\n'
                    '    <description>Foo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggsFoo bar spam eggs</description>\n\n\n'
                    '    <http-transactions>\n'
                    '            <http-transaction id="2">\n\n'
                    '    <http-request>\n'
                    '        <status>POST https://w4af.com/._basebind/node_modules/lodash._basecreate/LICENSE.txt%00=%DA%9E HTTP/1.1</status>\n'
                    '        <headers>\n'
                    '            <header field="User-agent" content="w4af" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">YT0x</body>\n'
                    '    </http-request>\n\n'
                    '    <http-response>\n'
                    '        <status>HTTP/1.1 200 OK</status>\n'
                    '        <headers>\n'
                    '            <header field="Content-Type" content="text/html" />\n'
                    '        </headers>\n'
                    '        <body content-encoding="base64">PGh0bWw+</body>\n'
                    '    </http-response>\n\n'
                    '</http-transaction>\n'
                    '    </http-transactions>\n'
                    '</vulnerability>')

        self.assertEqual(xml, expected)
        self.assertValidXML(xml)

    def test_is_generated_xml_valid(self):
        xml = ('''<vulnerability id="[14787]" method="GET" name="Strange HTTP response code" plugin="strange_http_codes" 
                   severity="Information" url="https://w4af.com/._basebind/node_modules/lodash._basecreate/LICENSE.txtZȨZȨ+k%s=ڞ"
                   var="None" vulndb_id="29">
                    - https://w4af.com/._basebind/node_modules/lodash._basecreate/LICENSE.txt<character code="0000"/>
                    <character code="0000"/><character code="0000"/><character code="0000"/>ZȨ<character code="0003"/>
                    <character code="000e"/>ZȨ<character code="0003"/><character code="000e"/><character code="0000"/>
                    <character code="0000"/><character code="0001"/><character code="0000"/>+k<character code="0000"/>
                    <character code="0000"/><character code="0000"/><character code="0000"/><character code="0000"/>
                    <character code="0000"/><character code="0000"/><character code="0000"/><character code="0000"/>
                    <character code="0000"/><character code="0000"/><character code="0000"/><character code="0004"/>%s=ڞ
                    
                    <status>GET https://w4af.com/._basebind/node_modules/lodash._basecreate/LICENSE.txt%00%00%00%00Z%C8
                    %A8%03%0EZ%C8%A8%03%0E%00%00%01%00+k%00%00%00%00%00%00%00%00%00%00%00%00%04%s=%DA%9E HTTP/1.1</status>
                    
                    </vulnerability>
                ''')
        self.assertValidXML(xml)


class TestFindingsCache(XMLNodeGeneratorTest):
    def setUp(self):
        kb.kb.cleanup()
        create_temp_dir()
        CachedXMLNode.create_cache_path()
        FindingsCache.create_cache_path()
        HistoryItem().init()

    def tearDown(self):
        remove_temp_dir()
        HistoryItem().clear()
        kb.kb.cleanup()

    def test_cache_works_as_expected(self):
        #
        # Cache starts empty
        #
        cache = FindingsCache()
        self.assertEqual(cache.list(), [])

        #
        # Create two vulnerabilities with their HTTP requests and responses
        #
        _id = 1

        name = 'I have a name'

        vuln1 = MockVuln(_id=_id)
        vuln1.set_name(name)

        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h1 = HistoryItem()
        h1.request = request
        res.set_id(_id)
        h1.response = res
        h1.save()

        _id = 2

        name = 'Just a name'

        vuln2 = MockVuln(_id=_id)
        vuln2.set_name(name)

        url = URL('http://w4af.com/a/b/c.php')
        hdr = Headers([('User-Agent', 'w4af')])
        request = HTTPRequest(url, data='a=1')
        request.set_headers(hdr)

        hdr = Headers([('Content-Type', 'text/html')])
        res = HTTPResponse(200, '<html>', hdr, url, url)

        h2 = HistoryItem()
        h2.request = request
        res.set_id(_id)
        h2.response = res
        h2.save()

        #
        # Save one vulnerability to the KB and call the cache-user
        #
        kb.kb.append('a', 'b', vuln1)

        x = xml_file()
        list(x.findings())

        self.assertEqual(cache.list(), [vuln1.get_uniq_id()])

        #
        # Save another vulnerability to the KB and call the cache-user
        #
        kb.kb.append('a', 'c', vuln2)

        list(x.findings())

        expected = {vuln1.get_uniq_id(), vuln2.get_uniq_id()}
        self.assertEqual(set(cache.list()), expected)

        #
        # Remove one vulnerability and see how it is removed from the cache
        #
        kb.kb.raw_write('a', 'c', 'noop')

        list(x.findings())

        expected = {vuln1.get_uniq_id()}
        self.assertEqual(set(cache.list()), expected)


class TestAttrValueEscapeFilter(unittest.TestCase):
    def test_invalid_ascii(self):
        result = jinja2_attr_value_escape_filter('é')

        self.assertIsInstance(result, str)
        self.assertEqual(result, 'é')

