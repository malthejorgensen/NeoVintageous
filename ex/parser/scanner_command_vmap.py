from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_VMAP
from .tokens_base import TokenOfCommand
from NeoVintageous import ex


@ex.command('vmap', 'vm')
class TokenCommandOmap(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_VMAP,
                         'vmap', *args, **kwargs)
        self.target_command = 'ex_vmap'

    @property
    def keys(self):
        return self.params['keys']

    @property
    def command(self):
        return self.params['command']


def scan_command_vmap(state):
    params = {
        'keys': None,
        'command': None,
    }

    m = state.match(r'\s*(?P<keys>.+?)\s+(?P<command>.+?)\s*$')

    if m:
        params.update(m.groupdict())

    return None, [TokenCommandOmap(params), TokenEof()]
