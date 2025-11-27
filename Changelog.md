# Changelog

All notable changes to `fastafiles.py` will be documented in this file.

## [0.2.0] - 2025-11-25 - Improvements made by Alan Rockefeller

### Added
- Command-line interface using `argparse` 
- `--debug` flag for verbose output to aid in troubleshooting.
- `--help` flag with a detailed explanation of script functionality and options.
- This `Changelog.md` file.

### Fixed
- The script no longer crashes when encountering GenBank records without sequence data (e.g., WGS projects). It now skips them safely.

### Changed
- The script was refactored to use a `main()` function.
- Argument parsing was updated from `sys.argv` to `argparse` so we can have better command like argument parsing.

## [0.1.0] - 2025-11-20 - Initial Version created by Hector Hind
- A script to search the NCBI nucleotide database.
- Downloads sequences and creates a FASTA file.
- Formats FASTA headers to `accession|organism|location`.
- Replaces spaces in the output file with underscores.
