Changelog
=========

0.0.4 (2025-07-03)
------------------

- added method `read_fp` to `SpectrumReader` and `write_fp` to `SpectrumWriter` to make use
  of file-like objects directly


0.0.3 (2025-06-25)
------------------

- added read/write support for spectra in CSV files (row-wise)
- added read/write support for spectra in ARFF files (row-wise)
- the ADAMS writer now outputs the Sample ID as well


0.0.2 (2025-06-18)
------------------

- fixed access of `output_sampledata` flag of ADAMS Writer
- added setter for sample data in `Spectrum` class
- the NIR Reader no longer skips the reference values
- serialization of constituents in FOSS NIR header is now more robust


0.0.1 (2025-04-14)
------------------

- initial release

