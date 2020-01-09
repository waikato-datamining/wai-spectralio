# wai-spectral-io
Python library for reading/writing various NIR, MIR, XRF spectral data formats.

## Supported formats

* [ADAMS](https://adams.cms.waikato.ac.nz/) spectra (.spec, .spec.gz)
* ...


## Usage

The code below uses the convenience methods `read` and `write` provided by the `wai.spectralio.adams`
module for handling ADAMS spectra: 

```python
from wai.spectralio.adams import read, write

sps = read("/some/where/data.spec.gz")
for sp in sps:
    print(sp)
    print(sp.waves())
    print(sp.amplitudes())
    print(sp.metadata())
write(sps, "/somewhere/else/blah.spec.gz")
```

If setting options is necessary, you can use the `Reader` and `Writer` and configure them:

```python
from wai.spectralio.adams import Reader, Writer

reader = Reader()
# set potential options
sps = reader.read("/home/fracpete/temp/dale.specconv/drystekker/OptimisationSet/Source/1NTA100175B19.spec.gz")
for sp in sps:
    print(sp)
    print(sp.waves())
    print(sp.amplitudes())
    print(sp.metadata())
writer = Writer()
# set potential options
writer.write(sps, "/home/fracpete/blah.spec.gz")
```
