import datetime
from typing import Optional, Type, List

from .api import SpectrumReader, SpectrumWriter, Spectrum
from .foss import *
from .foss.serialisers import FossFileSerialiser
from .mixins import ProductCodeOptionsMixin
from .options import Option


def datetime_helper(timestamp_string: Optional[str]) -> datetime:
    """
    Helper function for the timestamp option.

    :param timestamp_string:    The value given to the option, or None
                                if omitted.
    :return:                    The timestamp as a datetime object.
    """
    # Default value is now
    if timestamp_string is None:
        return datetime.datetime.now()

    # TODO: Support for ADAMS BaseDateTime strings.

    return datetime.datetime.fromisoformat(timestamp_string)


class Reader(SpectrumReader):
    # Options
    type_field = Option(help="Code|Field1|Field2|Field3|ID|[sample_type]", default="Code")
    id_field = Option(help="ID|Field1|Field2|Field3|[prefix]", default="ID")
    start = Option(help="spectrum number to start loading from", type=int, default=1)
    max = Option(help="maximum spectra to load", type=int, default=-1)

    def get_id(self, sample_header: SampleHeader, fname: str, num_deleted: int) -> str:
        """
        Gets the ID for a spectrum.

        :return:    ID.
        """
        id_field = self.id_field.lower()
        if id_field == "id":
            return sample_header.sample_no
        elif id_field == "field1":
            return sample_header.sample_id_1
        elif id_field == "field2":
            return sample_header.sample_id_2
        elif id_field == "field3":
            return sample_header.sample_id_3
        return self.id_field + fname + str(sample_header.sequence - num_deleted)

    def get_sample_type(self, sample_header: SampleHeader) -> str:
        """
        Gets the sample type for a spectrum.

        :return:    Sample type.
        """
        type_field = self.type_field.lower()
        if type_field == "code":
            return str(sample_header.product_code)
        elif type_field == "field1":
            return sample_header.sample_id_1
        elif type_field == "field2":
            return sample_header.sample_id_2
        elif type_field == "field3":
            return sample_header.sample_id_3
        elif type_field == "id":
            return sample_header.sample_no
        return self.type_field

    def get_wavenumbers(self, instrument_header: InstrumentHeader) -> List[float]:
        total_points = 0
        for segment in range(instrument_header.num_seg):
            total_points += instrument_header.points_per_segment[segment]

        # Can only handle EQLSPA
        if instrument_header.spacing_mode != 1:
            self.logger.warning(f"Can't process spacing mode {instrument_header.spacing_mode}")
            return list(map(float, range(total_points)))

        wavenumbers = []

        for i in range(instrument_header.num_seg):
            for j in range(instrument_header.points_per_segment[i]):
                wavenumbers.append(instrument_header.starts[i] + j * instrument_header.increments[i])

        return wavenumbers

    def _read(self, spec_file, filename):
        spectra = []

        ff = FossFileSerialiser().deserialise(spec_file)

        num_deleted = 0
        act_count = 0

        wavenumbers = self.get_wavenumbers(ff.instrument_header)

        for sh, db, cv, si in ff.samples:
            if sh.deleted:
                num_deleted += 1
                continue

            act_count += 1
            if act_count < self.start:
                continue

            id_ = self.get_id(sh, filename, num_deleted)
            if id_ == "":
                continue

            sampletype = self.get_sample_type(sh)
            if sampletype == "":
                continue

            if len(db.amplitudes) != len(wavenumbers):
                self.logger.warning("Different no. of wavenumbers and amplitudes")
                waves = list(map(float, range(len(db.amplitudes))))
            else:
                waves = wavenumbers

            ampls = db.amplitudes

            report = {}

            if ff.general_header.num_consts > 0:
                if ff.general_header.num_consts != len(ff.instrument_header.constituents):
                    self.logger.critical("Reference data is inconsistent")
                else:
                    for i, ref in enumerate(ff.instrument_header.constituents):
                        if cv.constituents[i] == 0.0:
                            continue

                        report[ref.lower()] = cv.constituents[i]

            spectra.append(Spectrum(id_, waves, ampls, report))

            if self.max != -1 and len(spectra) >= self.max:
                break

        return spectra

    def binary_mode(self, filename: str) -> bool:
        return True

    @classmethod
    def get_writer_class(cls) -> 'Type[Writer]':
        return Writer


class Writer(ProductCodeOptionsMixin, SpectrumWriter):
    """
    Writer that stores spectrums in the FOSS .nir Format.
    """
    # Options
    instrument_name = Option(help="instrument name", default="<not implemented>")
    client = Option(help="client of sample", default="client")
    file_id = Option(help="file ID", default="generated by wai.spectralio")
    sample_id_1 = Option(help="sample ID 1", default="")
    sample_id_2 = Option(help="sample ID 2", default="")
    sample_id_3 = Option(help="sample ID 3", default="")
    serial_no = Option(help="serial number of instrument", default="0000-0000-0000")
    master = Option(help="serial number of master instrument", default="0000-0000-0000")
    operator = Option(help="instrument operator", default="wai.spectralio")
    segment_widths = Option(help="width of segments", type=int, default=[1050], nargs='+')
    start_points = Option(help="start points of segments", type=float, default=[400.0], nargs='+')
    increments = Option(help="wave increments", type=float, default=[2.0], nargs='+')
    end_points = Option(help="end points of segments", type=float, default=[1098.0], nargs='+')
    EOC = Option(help="number of EOCs per rev", type=int, default=0)
    timestamp = Option(help="the timestamp to use in the file", type=datetime_helper, default=None)

    def get_creation_date(self) -> datetime.date:
        """
        Gets the creation date.

        :return: The creation date.
        """
        # TODO: Actual implementation
        return datetime.date.today()

    def get_general_header(self, data: List[Spectrum]) -> GeneralHeader:
        """
        Create general header from list of spectra.

        :param data:    The list of spectra.
        :return:        The general header.
        """
        gh = GeneralHeader()
        gh.type = 1
        gh.count = len(data)
        gh.deleted = 0
        gh.num_points = len(data[0].waves)
        gh.num_consts = 0
        gh.creation_date = self.get_creation_date()
        gh.time = datetime.datetime(gh.creation_date.year, gh.creation_date.month, gh.creation_date.day)
        gh.most_recent = 0
        gh.file_id = self.file_id
        gh.master = self.master

        return gh

    def get_instrument_header(self) -> InstrumentHeader:
        """
        Creates instrument header using parameters.

        :return:    Instrument header.
        """
        ih = InstrumentHeader()

        ih.instrument_type = InstrumentType.SIC_6500
        ih.model = self.instrument_name
        ih.serial = self.serial_no
        ih.num_seg = len(self.segment_widths)
        ih.points_per_segment = [self.segment_widths[i] for i in range(ih.num_seg)]
        ih.points_per_segment += [0] * (20 - len(ih.points_per_segment))
        ih.spacing_mode = 1
        ih.wave = self.start_points[:7]
        ih.wave += [0.0] * (7 - len(ih.wave))
        ih.wave += self.increments[:7]
        ih.wave += [0.0] * (14 - len(ih.wave))
        ih.wave += self.end_points[:7]
        ih.wave += [0.0] * (21 - len(ih.wave))
        ih.neoc = self.EOC
        ih.constituents = [""] * 32

        return ih

    def get_sample_header(self, sp: Spectrum, pos: int) -> SampleHeader:
        """
        Create a SampleHeader from a Spectrum and position in list/file.

        :param sp:      Spectrum.
        :param pos:     Position.
        :return:        Sample header.
        """
        sh = SampleHeader()

        sh.sample_no = sp.id.replace("'", "")
        sh.sequence = pos
        sh.deleted = False
        sh.creation_date = self.get_creation_date()
        sh.time = datetime.datetime(sh.creation_date.year, sh.creation_date.month, sh.creation_date.day)

        pcode: str = self.product_code
        if self.product_code_from_field:
            report = sp.sample_data
            if report is None:
                pcode = "<Report Not Available>"
            else:
                if pcode not in report:
                    pcode = f"<Field '{pcode}' Not Available in Report>"
                else:
                    pcode = str(report[pcode])
        try:
            sh.product_code = int(pcode)
        except ValueError:
            self.logger.exception(f"Product code ({pcode}) is non-numeric, or not present")

        sh.client = self.client
        sh.operator = self.operator
        sh.sample_id_1 = self.sample_id_1
        sh.sample_id_2 = self.sample_id_2
        sh.sample_id_3 = self.sample_id_3
        sh.standardised = 0

        return sh

    def get_data_block(self, sp: Spectrum) -> DataBlock:
        """
        Create a data-block from a spectrum.

        :param sp:  Spectrum.
        :return:    The data block.
        """
        db = DataBlock()
        db.amplitudes = sp.amplitudes
        return db

    def get_constituent_values(self, sp: Spectrum) -> ConstituentValues:
        """
        Create ConstituentValues for a spectrum.

        :param sp:  Spectrum.
        :return:    Constituent values.
        """
        return ConstituentValues()

    def get_sample_info(self, sp: Spectrum, pos: int) -> SampleInfo:
        """
        Create a SampleInfo for the file footer based on a Spectrum and it's position in list/file.

        :param sp:      Spectrum.
        :param pos:     Position.
        :return:        SampleInfo.
        """
        si = SampleInfo()

        si.deleted = False
        si.sample_id = sp.id.replace("'", "")
        si.sequence = pos

        return si
        
    def _write(self, spectra, spec_file, as_bytes):
        ff = FossFile(
            self.get_general_header(spectra),
            self.get_instrument_header(),
            list(
                (self.get_sample_header(spectrum, i),
                 self.get_data_block(spectrum),
                 self.get_constituent_values(spectrum),
                 self.get_sample_info(spectrum, i))
                for i, spectrum in enumerate(spectra)))

        FossFileSerialiser().serialise(ff, spec_file)

    @classmethod
    def get_reader_class(cls) -> Type[Reader]:
        return Reader

    def binary_mode(self, filename: str) -> bool:
        return True


read = Reader.read


write = Writer.write
