import csv

def process_file(input_filename, output_filename):
    # Open the input file for reading and output file for writing.
    with open(input_filename, 'r', newline='') as infile, open(output_filename, 'w', newline='') as outfile:
        # Assuming the input file is tab-delimited.
        reader = csv.DictReader(infile, delimiter='\t')
        for row in reader:
            # Create the new string in the desired format:
            # RrefAA + PP + AltAA
            new_value = f"{row['RrefAA']}{row['PP']}{row['AltAA']}"
            outfile.write(new_value + '\n')

if __name__ == '__main__':
    # Change these file names as needed.
    input_file = 'mutpot1.txt'
    output_file = 'output_file.txt'
    process_file(input_file, output_file)
    print(f"Processing complete. Output written to {output_file}")
