# wai-spectral-io
Python library for reading/writing various NIR, MIR, XRF spectral data formats.

## Supported formats

* [ADAMS](https://adams.cms.waikato.ac.nz/) spectra (.spec, .spec.gz)
* ...


## API

The following classes are defined by the API:

* `wai.spectralio.Spectrum` -- simple container for spectral data and associated sample data
* `wai.spectralio.OptionHandler` -- superclass for classes that require option-handling/parsing
* `wai.spectralio.SpectrumReader` -- superclass for spectral data readers (derived from `wai.spectralio.OptionHandler`)
* `wai.spectralio.SpectrumWriter` -- superclass for spectral data writers (derived from `wai.spectralio.OptionHandler`)

Classes derived from `wai.spectralio.OptionHandler` can output help for the supported options
via the `options_help()` method. 


## Examples

The code below uses the convenience methods `read` and `write` provided by the `wai.spectralio.adams`
module for handling ADAMS spectra: 

```python
from wai.spectralio.adams import read, write

sps = read("/some/where/data.spec.gz", options=["--keep_format"])
for sp in sps:
    print(sp.id)
    print("  ", sp.waves)
    print("  ", sp.amplitudes)
    print("  ", sp.sampledata)
write(sps, "/somewhere/else/blah.spec.gz", options=["--output_sampledata"])
```

These two methods construct `Reader`/`Writer` objects on the fly and parse the supplied options. 
Of course, you can use the `Reader` and `Writer` classes directly, e.g., when reusing the
same object multiple times:

```python
from wai.spectralio.adams import Reader, Writer

reader = Reader()
reader.options = ["--keep_format"]
sps = reader.read("/some/where/data.spec")
for sp in sps:
    print(sp.id)
    print("  ", sp.waves)
    print("  ", sp.amplitudes)
    print("  ", sp.sampledata)
writer = Writer()
writer.options = ["--output_sampledata"]
writer.write(sps, "/somewhere/else/blah.spec.gz")
```
