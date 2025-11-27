# Fastafiles

`Fastafiles` is a simple Python tool to retrieve FASTA files from GenBank (via NCBI) using Biopython.  
It is designed for easy batch-downloads of nucleotide sequences for phylogenetic or sequence analysis.

- Query the NCBI nucleotide database with a search term (organism name, gene name, or combination)  
- Automatically fetch sequence records in GenBank format  
- Extract sequences and metadata (organism name, location if available)  
- Write a clean FASTA file with headers containing accession, organism, and location  
- Replace spaces in headers with underscores (“_”) to avoid downstream issues (e.g., with alignment or phylogeny software)  
- Minimal dependencies (only `Bio` / Biopython + Python standard library)

## Requirements

- Python 3.x  
- [Biopython](https://biopython.org/) — make sure it is installed (`pip install biopython`)  

## TO-DO

- Default to ITS if no user input is given
- Add a "confirmed observation mode" that only gets records that have inaturalist or mushroomobserver links with photos  
- BLAST mode that returns the top 100 results from a known observation
 
## Usage

```bash
python fastafiles.py 'Your_query_here' --email youremail@mail.com --max-results 9000
