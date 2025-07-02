# wai-spectral-io
Python library for reading/writing various NIR, MIR, XRF spectral data formats.


## Supported formats

* [ADAMS](https://adams.cms.waikato.ac.nz/) spectra (.spec, .spec.gz)
* [ARFF](https://waikato.github.io/weka-wiki/formats_and_processing/arff_syntax/) (row-wise)
* ASC
* ASCII XY
* CAL (FOSS)
* CSV (row-wise)
* DPT
* MPS (XRF)
* NIR (FOSS)
* OPUS (Bruker)
* OPUS ext (Bruker)
* SPA (Thermo Scientific)


## Installation

Via PyPI:

```bash
pip install wai_spectralio
```

The latest code straight from the repository:

```bash
pip install git+https://github.com/waikato-datamining/wai-spectralio.git
```


## API

The following classes are defined by the API:

* `wai.spectralio.options.OptionHandler` -- superclass for classes that require option-handling/parsing
* `wai.spectralio.options.Option` -- for defining an option within a Reader/Writer
* `wai.spectralio.api.Spectrum` -- simple container for spectral data and associated sample data
* `wai.spectralio.api.SpectrumReader` -- superclass for spectral data readers (implements `wai.spectralio.options.OptionHandler`)
* `wai.spectralio.api.SpectrumWriter` -- superclass for spectral data writers (implrements `wai.spectralio.options.OptionHandler`)

Classes derived from `wai.spectralio.options.OptionHandler` can output help for the supported options
via the `options_help()` method. 


## Examples

The code below uses the convenience methods `read` and `write` provided by the `wai.spectralio.adams`
module for handling ADAMS spectra: 

```python
from wai.spectralio.adams import read, write

sps = read("/some/where/data.spec.gz", options=["--keep-format"])
for sp in sps:
    print(sp.id)
    print("  ", sp.waves)
    print("  ", sp.amplitudes)
    print("  ", sp.sample_data)
write(sps, "/somewhere/else/blah.spec.gz", options=["--output-sampledata"])
```

These two methods construct `Reader`/`Writer` objects on the fly and parse the supplied options. 
Of course, you can use the `Reader` and `Writer` classes directly, e.g., when reusing the
same object multiple times:

```python
from wai.spectralio.adams import Reader, Writer

reader = Reader()
reader.options = ["--keep-format"]
sps = reader.read("/some/where/data.spec")
for sp in sps:
    print(sp.id)
    print("  ", sp.waves)
    print("  ", sp.amplitudes)
    print("  ", sp.sample_data)
writer = Writer()
writer.options = ["--output-sampledata"]
writer.write(sps, "/somewhere/else/blah.spec.gz")
```

For converting between two formats, simply choose the appropriate Reader/Writer
class (or read/write method). E.g., for ADAMS to FOSS CAL use this:

```python
import os
from wai.spectralio.adams import Reader
from wai.spectralio.cal import Writer

reader = Reader()
reader.options = ["--keep-format"]
full = []
path = "/some/where"
for f in os.listdir(path):
    if f.endswith(".spec"):
        sps = reader.read(os.path.join(path, f))
        full.extend(sps)
writer = Writer()
writer.constituents = ["ref_1", "ref_2"]  # the names of the sample data fields to store in the .cal file
writer.write(full, "/else/where/blah.cal")
```

It is also possible to read from and write to file-like objects directly using
the following methods:

* SpectrumReader: `read_fp`
* SpectrumWriter: `write_fp`
