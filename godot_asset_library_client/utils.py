import yaml
from pygments import highlight
from pygments.lexers import YamlLexer
from pygments.formatters import TerminalFormatter


def pretty(data):
    code = yaml.dump(data)
    return highlight(code, YamlLexer(), TerminalFormatter())


