class SampleInfo:
    """
    Sample Info.
    """
    def __init__(self):
        # String(13): zero terminated. Sample name
        self.sample_id: str = ""

        # 2 BYTE? Sequence number in file
        self.sequence: int = 0

        # 1 BYTE? Deleted?
        self.deleted: bool = False
