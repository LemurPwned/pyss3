# ChangeLog

All notable changes to PySS3 will be documented here.

## [0.3.9] 2019-11-27

### Added
- Live Test: layout updated.
- PySS3 Command Line: ``frange`` function added as an alias of ``r`` for the ``grid_search`` command.

### Fixed
- PySS3 Command Line: live_test always lunch the server with no documents (even when before "live_test a/path")
- Live Test:sentences starting with "unknown" token were not included in the "Advanced" interactive chart


## [0.3.8] 2019-11-25

### Fixed
- Server: fixed bug that stopped the server when receiving arbitrary bytes (not utf-8 strings)
- PySS3 Command Line: fixed bug when loading live_test with a non existing path
- Live Test: now the user can select single letter words (and are also included in the "advanced" live chart)


## [0.3.7] 2019-11-22

### Added
- Summary operators are not longer static.
- ``Server.set_testset_from_files`` lazy load.

### Fixed
- Evaluation plot: confusion matrices size when working with k-folds


## [0.3.6] 2019-11-14

### Added
- `Dataset` class added to `pyss3.util` as an interface to help the user to load/read datasets. Method `Dataset.load_from_files` added
- Documentations updated


## [0.3.5] 2019-11-12

### Added
- PySS3 Command Line Python 2 full compatibility support

### Fixed
- Matplotlib set_yaxis bug fixed


## [0.3.4] 2019-11-12

### Fixed
- Dependencies and compatibility with python 2 Improved


## [0.3.3] 2019-11-12

### Fixed
- Setup and tests fixed


## [0.3.2] 2019-11-12

### Added
- Summary operators: now it is possible to use user-defined summary operators, the following static methods were added to the ``SS3`` class: `summary_op_ngrams`, `summary_op_sentences`, and `summary_op_paragraphs`.


## [0.3.1] 2019-11-11

### Added
- update: some docstrings were improved
- update: the README.md / Pypi Description file.

### Fixed
- Python 2 and 3 compatibility problem with scikit-learn (using version 0.20.1 from now on)
- PyPi: setup.py: `long_description_content_type` set to `'text/markdown'`