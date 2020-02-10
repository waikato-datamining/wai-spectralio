import datetime


class GeneralHeader:
    """
    General header.
    """
    def __init__(self):
        # 2 BYTES: Use 1st BYTE. 01=.NIR, 02=.CAL
        self.type: int = 1

        # 2 BYTES: number of (non deleted) spectra
        self.count: int = 0

        # 2 BYTES: number of (deleted) spectra
        self.deleted: int = 0

        # 2 BYTES:number of spectral data points
        self.num_points: int = 0

        # 2 BYTES: number of constituents
        self.num_consts: int = 0

        # 2 BYTES: unsigned int. Creation date
        self.creation_date: datetime.date = datetime.date.today()

        # 4 BYTES: long int. Time
        self.time: datetime.datetime = datetime.datetime.now()

        # 2 BYTES: CHK file? Use 00
        self.most_recent: int = 0

        # char[71] file id
        self.file_id: str = ""

        # char[9] master serial no
        self.master: str = ""

        # char[30] packing info
        self.packing: str = ""
