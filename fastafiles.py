from Bio import Entrez, SeqIO
import time
import sys

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
query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "psilocybe zapotecorum AND ITS1"
filename = "%s.fasta" % query
# TODO - search for "AND" and continue or default to ITS

# Search NCBI database - retmax == results , up to 10,000 :0 
search_handle = Entrez.esearch(db="nucleotide", term=query, retmax=8)
search_results = Entrez.read(search_handle)
search_handle.close()
# just being polite as the API ask's for 0.3
time.sleep(0.5)

# Get the list of IDs
ids = search_results["IdList"]
if not ids:
    print(f"No sequences found for your query for {filename}.")
    exit()
    
print(f"Found {len(ids)} sequences: {ids}")

# find the sequences in GenBank format so we can access metadata
fetch_handle = Entrez.efetch(db="nucleotide", id=",".join(ids), rettype="gb", retmode="text")
gb_records = list(SeqIO.parse(fetch_handle, "genbank"))
fetch_handle.close()
time.sleep(0.5)

fasta_records = []

for record in gb_records:

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
