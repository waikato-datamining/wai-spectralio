import datetime


class SampleHeader:
    """
    Sample Header.
    """
    def __init__(self):
        # String(13): zero terminated. Sample name
        self.sample_no: str = ""

        # 2 BYTE? Sequence number in file
        self.sequence: int = 0

        # 1 BYTE?? Deleted?
        self.deleted: bool = False

        # 2 BYTES: unsigned int. date
        self.date: datetime.date = datetime.date.today()

        # 2 BYTES: unsigned int. code
        self.product_code: int = 0

        # String(9): zero terminated. Client
        self.client: str = ""

        # String(151): zero terminated. Sample id. (divided into 3?)
        # SampleID #1
        self.sample_id_1: str = ""

        # SampleID #2
        self.sample_id_2: str = ""

        # SampleID #3
        self.sample_id_3: str = ""

        # String(32): zero terminated. operator
        self.operator: str = ""

        # 2 BYTE?? Standardised?
        self.standardised: int = 0

        # Sample time
        self.time: datetime.datetime = datetime.datetime.now()

        # 38 bytes of padding
