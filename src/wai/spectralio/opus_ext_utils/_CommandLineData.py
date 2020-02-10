from typing import Dict

from ..api import LoggingObject
from .constants import KEYWORD_CMDLINE


class CommandLineData(LoggingObject):
    """
    Encapsulates and parses a commandline string.
    """
    def __init__(self, raw: str):
        self.raw: str = raw
        self.operation: str = ""
        self.type: str = ""
        self.values: Dict[str, str] = {}

        try:
            self.parse()
        except Exception:
            self.logger.exception(f"Failed to parse: {raw}")

    def parse(self):
        """
        Parses the command line.
        """
        self.values = {}
        intro = self.raw[:self.raw.index('(')]
        payload = self.raw[self.raw.index('(') + 1:self.raw.rindex(')')]
        self.operation = intro[intro.index(KEYWORD_CMDLINE) + len(KEYWORD_CMDLINE):].strip()
        self.type = payload[payload.index('[') + 1:payload.index(']')].replace('"::this::":', '')
        data = payload[payload.index('{') + 1:payload.rindex('}')]

        current = ""
        escaped = False
        pairs = []
        for i, c in enumerate(data):
            if c == "'":
                escaped = not escaped
            elif c == ",":
                if not escaped:
                    if len(current) > 0:
                        pairs.append(current.strip())
                    current = ""
                else:
                    current += c
            else:
                current += c

        # Left-over?
        if len(current) > 0:
            pairs.append(current.strip())

        # Split into key-value pairs
        for pair in pairs:
            if '=' in pair:
                key = pair[:pair.index('=')]
                value = pair[pair.index('=') + 1:]
                self.values[key.strip()] = value.strip()
            else:
                self.logger.warning(f"Invalid key-value pair: '{pair}'")

    def __len__(self):
        return len(self.values)

    def keys(self):
        return self.values.keys()

    def has(self, key: str) -> bool:
        return key in self.values

    def get(self, key: str) -> str:
        return self.values[key]

    def __str__(self):
        return f"operation={self.operation}, type={self.type}, values={self.values}"
