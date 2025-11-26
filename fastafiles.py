
from Bio import Entrez, SeqIO
from Bio.Seq import UndefinedSequenceError
import time
import argparse

def main():
    parser = argparse.ArgumentParser(
        description=(
            "This script searches the NCBI Nucleotide database, fetches sequence data, "
            "and saves it to a FASTA file. It's designed for researchers to quickly "
            "retrieve genetic sequence information from NCBI with customizable FASTA "
            "headers. Key features include extracting organism and location metadata, "
            "formatting the output, and cleaning up headers by replacing spaces "
            "with underscores for compatibility with bioinformatics tools."
        ),
        epilog=(
            "Output File Naming: The output FASTA filename is derived directly "
            "from your search query. For example, a query 'fungus ITS region' "
            "will result in 'fungus ITS region.fasta'.\n\n"
            "FASTA Header Format: Each FASTA header is formatted as "
            "`accession|organism|location`. The location is extracted by "
            "preferring 'country' then 'geo_loc_name' from the GenBank record's "
            "source feature.\n\n"
            "Space Replacement: All spaces in the generated FASTA headers (and "
            "filename) are automatically replaced with underscores to ensure "
            "compatibility with various bioinformatics tools (e.g., MEGA, MAFFT) "
            "that may misinterpret spaces in identifiers."
        ),
        formatter_class=argparse.RawTextHelpFormatter # Use RawTextHelpFormatter to preserve newlines in epilog
    )
    parser.add_argument(
        'query_terms',
        nargs='*',
        help=(
            "The specific terms used to search the NCBI Nucleotide database. "
            "Provide your search terms directly after the script name. If your "
            "query contains spaces, enclose it in quotes (e.g., 'Homo sapiens 18S rRNA'). "
            "If no query terms are provided, the script defaults to searching for "
            "'psilocybe zapotecorum AND ITS1'.\n"
            "Example: python fastafiles.py 'fungus ITS region'"
        )
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help=(
            "Enable verbose logging and debug information. When enabled, the script "
            "will print the exact query sent to NCBI, the raw search results, "
            "the parsed GenBank records, and details about how each sequence record "
            "is processed before being written to the FASTA file. This is useful "
            "for troubleshooting or understanding the script's internal operations."
        )
    )
    args = parser.parse_args()

    #*************DEFINES*************
    def remove_spaces(filepath):
        # Replace spaces with underscores in the output FASTA file
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        modified_lines = [line.replace(' ', '_') for line in lines]
        
        with open(filepath, 'w') as f:
            f.writelines(modified_lines)
    #************/DEFINES*************

    # Yo NCBI dis is me
    Entrez.email = "justarandomemailaddress@gmail.com"

    # search for a gene or sequence or both with AND ie "your thing AND ITS1"
    query = " ".join(args.query_terms) if args.query_terms else "psilocybe zapotecorum AND ITS1"
    if args.debug:
        print(f"DEBUG: Sending query: '{query}'")

    filename = "%s.fasta" % query
    # TODO - search for "AND" and continue or default to ITS

    # Search NCBI database - retmax == results , up to 10,000 :0 
    search_handle = Entrez.esearch(db="nucleotide", term=query, retmax=8)
    search_results = Entrez.read(search_handle)
    search_handle.close()
    if args.debug:
        print(f"DEBUG: Received search results: {search_results}")

    # just being polite as the API ask's for 0.3
    time.sleep(0.5)

    # Get the list of IDs
    ids = search_results["IdList"]
    if not ids:
        if args.debug:
            print("DEBUG: The 'IdList' in the search result was empty. Cannot proceed.")
        print(f"No sequences found for your query for {filename}.")
        exit()
        
    print(f"Found {len(ids)} sequences: {ids}")

    # find the sequences in GenBank format so we can access metadata
    fetch_handle = Entrez.efetch(db="nucleotide", id=",".join(ids), rettype="gb", retmode="text")
    gb_records = list(SeqIO.parse(fetch_handle, "genbank"))
    fetch_handle.close()
    if args.debug:
        print(f"DEBUG: Received and parsed {len(gb_records)} GenBank records. Data received:")
        # The default repr for SeqRecord is informative enough for debug
        print(gb_records)
    time.sleep(0.5)

    fasta_records = []

    for record in gb_records:

        # Skip records that have no sequence data by catching the error that
        # would be raised if we tried to access it.
        try:
            # The str() conversion will fail with UndefinedSequenceError
            # on records like WGS projects.
            str(record.seq)
        except (UndefinedSequenceError, TypeError):
            if args.debug:
                print(f"DEBUG: Skipping record {record.id} because its sequence content is undefined.")
            continue

        # default if metadata missing
        location = "Unknown"

        # Extract metadata from source feature
        for feature in record.features:
            if feature.type == "source":
                q = feature.qualifiers

                # If "country" exists, use it
                if "country" in q:
                    location = q["country"][0]
                
                # Otherwise use "geo_loc_name"
                elif "geo_loc_name" in q:
                    location = q["geo_loc_name"][0]

                break

        organism = record.annotations.get("organism", "Unknown")

        # Build new FASTA header: accession|organism|location
        new_id = f"{record.id}|{organism}|{location}"

        if args.debug:
            print(f"DEBUG: Processing record {record.id}:")
            print(f"  - Organism: {organism}")
            print(f"  - Location: {location}")
            print(f"  - New Header: {new_id}")

        # Create simplified FASTA record
        new_record = SeqIO.SeqRecord(
            record.seq,
            id=new_id,
            description=""
        )

        fasta_records.append(new_record)

    # Save dat shit
    with open(filename, "w") as out_file:
        SeqIO.write(fasta_records, out_file, "fasta")

    # Edit dat shit - Replace spaces with _ otherwise MEGA and others mess with the name
    remove_spaces(filename)
    # TODO - clean up records to include just names,gene,location & filename to disclude "AND" 

    print(f"Saved {len(fasta_records)} sequences to {filename}")

if __name__ == "__main__":
    main()

