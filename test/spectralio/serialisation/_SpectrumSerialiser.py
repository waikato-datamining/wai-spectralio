from typing import IO, Optional

from wai.test.serialisation import RegressionSerialiser

from wai.spectralio.api import Spectrum


class SpectrumSerialiser(RegressionSerialiser[Spectrum]):
    """
    Serialises a spectrum.
    """
    @classmethod
    def binary(cls) -> bool:
        return False

    @classmethod
    def extension(cls) -> str:
        return "specref"

    @classmethod
    def serialise(cls, result: Spectrum, file: IO[str]):
        # Write the ID
        file.write(f"{result.id}\n")

        # Write the waves and amplitudes
        for wave, ampl in zip(result.waves, result.amplitudes):
            file.write(f"d {wave},{ampl}\n")

        # Write the sample data
        for key, value in result.sampledata.items():
            value = f"'{value}'" if isinstance(value, str) else str(value)
            file.write(f"s {key}={value}\n")

    @classmethod
    def deserialise(cls, file: IO[str]) -> Spectrum:
        # Read the ID
        id = file.readline()[:-1]

        # Read the waves and amplitudes
        waves, ampls = [], []
        line = file.readline()
        while line.startswith("d "):
            wave, ampl = line[2:-1].split(',')
            wave, ampl = float(wave), float(ampl)
            waves.append(wave)
            ampls.append(ampl)
            line = file.readline()

        # Read the sample data
        sampledata = {}
        while line.startswith("s "):
            key, value = line[2:-1].split("=", 1)
            if value.startswith("'"):
                value = value[1:-1]
            elif value == str(True):
                value = True
            elif value == str(False):
                value = False
            else:
                value = float(value)
            sampledata[key] = value
            line = file.readline()

        return Spectrum(id, waves, ampls, sampledata)

    @classmethod
    def compare(cls, result: Spectrum, reference: Spectrum) -> Optional[str]:
        if result.id != reference.id:
            return f"Result ID '{result.id}' doesn't match reference ID '{reference.id}'"

        num_result_waves = len(result.waves)
        num_ref_waves = len(reference.waves)
        if num_result_waves != num_ref_waves:
            return (f"Result and reference have different number of samples "
                    f"({num_result_waves} vs. {num_ref_waves})")

        for i, result_wave, result_ampl, ref_wave, ref_ampl in zip(range(num_ref_waves),
                                                                   result.waves, result.amplitudes,
                                                                   reference.waves, reference.amplitudes):
            if result_wave != ref_wave:
                return f"Wave numbers differ at position {i} ({result_wave} vs. {ref_wave})"

            if result_ampl != ref_ampl:
                return f"Amplitudes differ at position {i} ({result_ampl} vs. {ref_ampl})"

        if result.sampledata != reference.sampledata:
            return "Sample data differs"

        return None
