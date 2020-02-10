class BlockDefinition:
    """
    Container class for Opus block definitions in the header.
    """
    def __init__(self):
        self.type: int = 0
        self.length_blocks: int = 0
        self.length_bytes: int = 0
        self.offset: int = 0

    def __str__(self):
        return f"type={self.type}, lenBlocks={self.length_blocks}, lenBytes={self.length_bytes}, offset={self.offset}"
