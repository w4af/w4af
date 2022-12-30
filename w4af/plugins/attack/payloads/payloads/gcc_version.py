import re
from w4af.plugins.attack.payloads.base_payload import Payload
from w4af.core.ui.console.tables import table

MATCH_EXPRESSIONS = [
    r'(?<=gcc version ).*?\)|(gcc-(\d+ (\([^\)]+\) )*[^\)]+))\)',
    r'(gcc (\([^\)]+\) )*[^\)]+)\)'
]

class gcc_version(Payload):
    """
    This payload shows the current GCC Version
    """
    def parse_gcc_version(self, proc_version):
        for expr in MATCH_EXPRESSIONS:
            gcc_version = re.search(expr, proc_version)
            if gcc_version:
                return gcc_version.group(0)
        return ''

    def api_read(self):
        result = {}

        version = self.parse_gcc_version(self.shell.read('/proc/version'))
        if version:
            result['gcc_version'] = version

        return result

    def run_read(self):
        api_result = self.api_read()

        if not api_result['gcc_version']:
            return 'GCC version could not be identified.'
        else:
            rows = []
            rows.append(['GCC Version', api_result['gcc_version']])
            result_table = table(rows)
            result_table.draw(80)
            return rows
