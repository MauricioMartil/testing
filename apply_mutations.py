def apply_mutations(sequence, mutations):
    """
    Apply a list of mutations to a protein sequence.
    
    Each mutation should be provided in the format 'A12V' where:
      - 'A' is the expected residue at that position in the wild-type sequence,
      - '12' is the 1-indexed position,
      - 'V' is the residue to mutate to.
    
    Parameters:
        sequence (str): The original protein sequence.
        mutations (list of str): List of mutation strings.
    
    Returns:
        str: The mutated protein sequence.
    """
    # Convert the sequence to a list for easier modification.
    seq_list = list(sequence)
    
    for mutation in mutations:
        # Extract the expected original, position (as string), and new residue.
        original = mutation[0]
        new = mutation[-1]
        pos_str = mutation[1:-1]
        
        # Convert position to an index (assuming the mutations use 1-indexed positions).
        try:
            pos = int(pos_str) - 1  # Convert to 0-index.
        except ValueError:
            print(f"Invalid mutation format for {mutation}. Position '{pos_str}' must be an integer.")
            continue
        
        # Verify that the position is within the sequence.
        if pos < 0 or pos >= len(seq_list):
            print(f"Position {pos+1} in mutation {mutation} is out of range for the sequence length {len(seq_list)}.")
            continue
        
        # Check that the current residue matches the expected original.
        if seq_list[pos] != original:
            print(f"Warning: At position {pos+1}, expected '{original}' but found '{seq_list[pos]}'. Applying mutation anyway.")
        
        # Apply the mutation.
        seq_list[pos] = new
    
    # Join the list back into a string.
    return "".join(seq_list)


# Example usage:
protein_sequence = ("MSLVPATNYIYTPLNQLKGGTIVNVYGVVKFFKPPYLSKGTDYCSVVTIVDQTNVKLTCLLFSGNYEALPIIYKNGDIV"
                    "RFHRLKIQVYKKETQGITSSGFASLTFEGTLGAPIIPRTSSKYFNFTTEDHKMVEALRVWASTHMSPSWTLLKLCDVQPM"
                    "QYFDLTCQLLGKAEVDGASFLLKVWDGTRTPFPSWRVLIQDLVLEGDLSHIHRLQNLTIDILVYDNHVHVARSLKVGSF"
                    "LRIYSLHTKLQSMNSENQTMLSLEFHLHGGTSYGRGIRVLPESNSDVDQLKKDLESANLTANQHSDVICQSEPDDSFPS"
                    "SGSVSLYEVERCQQLSATILTDHQYLERTPLCAILKQKAPQQYRIRAKLRSYKPRRLFQSVKLHCPKCHLLQEVPHEGD"
                    "LDIIFQDGATKTPDVKLQNTSLYDSKIWTTKNQKGRKVAVHFVKNNGILPLSNECLLLIEGGTLSEICKLSNKFNSVIP"
                    "VRSGHEDLELLDLSAPFLIQGTIHHYGCKQCSSLRSIQNLNSLVDKTSWIPSSVAEALGIVPLQYVFVMTFTLDDGTG"
                    "VLEAYLMDSDKFFQIPASEVLMDDDLQKSVDMIMDMFCPPGIKIDAYPWLECFIKSYNVTNGTDNQICYQIFDTTVAEDVI")

# List your mutations here (example mutations)
#mutations = [
#    "Q94H", 
#    "Q94R",
#    "W139C",
#    "R137H",
#    "Y89C",
#    "Y36C",
#    "M251L"
#]

# Apply each mutation individually and print the mutated sequence.
#for mutation in mutations:
#    mutated_sequence = apply_mutations(protein_sequence, [mutation])  # Note: passing a list containing only one mutation
#    print(f"Mutated Sequence for mutation {mutation}:")
#    print(mutated_sequence)
#    print("-" * 50)  # Separator for better readability

# List your mutations here (example mutations)
# Read mutations from file
mutations = []
try:
    with open("output_file.txt", "r") as f:
        for line in f:
            mutation = line.strip()  # Remove leading/trailing whitespace
            if mutation:  # Ensure the line is not empty
                mutations.append(mutation)
except FileNotFoundError:
    print("Error: output_file.txt not found.")
except Exception as e:
    print(f"An error occurred: {e}")

# Apply each mutation individually and print the mutated sequence.
for mutation in mutations:
    mutated_sequence = apply_mutations(protein_sequence, [mutation])
    
    # Write the mutated sequence to a file
    try:
        with open("mutated_sequences.txt", "a") as outfile:  # Open in append mode
            outfile.write(f"Mutated Sequence for mutation {mutation}:\n")
            outfile.write(mutated_sequence + "\n")
            outfile.write("-" * 50 + "\n")  # Separator for better readability
    except Exception as e:
        print(f"An error occurred while writing to file: {e}")
