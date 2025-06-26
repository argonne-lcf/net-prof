# Changelog:

## [0.1.2] - 06-26-2025
### Added
- Multi-interface profiling
    - Retrofitted old collect() into helper function _collect_one_interface().
    - Changes to collect() to allow multi-interface, while using _collect_one_interface() for single interface profiling.
- introduced new test, test_iface_all.py

### Fixed
- Typo in __init__.py -- '.' in place of ','
- Typo in README.md -- 'import net-prof' to 'import net_prof'

## [0.1.1] - 06-25-2025
### Added
- CHANGELOG.md

### Fixed
- Got rid of Changelog from README.md.
- Forgot to update README.md before uploading to PYpi
- Didn't tag to github first for 0.1.0 so doing that now



## [0.1.0] - 06-25-2025
- Initial PyPI release
### Added
- Uploaded to pypi: https://pypi.org/project/net-prof/0.1.0/
- Changes to README.md

### Fixed
- Removed requirements.txt -- replaced with [dependencies] in .toml
- Added [dependencies] to pyproject.toml -- will be auto-installed with 'pip install net-prof'

