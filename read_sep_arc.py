import subprocess

def read_tinker_xyz(arc_file):
    """
    Reads a TINKER XYZ file and returns a list of atoms.
    """
    try:
        with open (arc_file, 'r') as file:
            try:
                n_atoms = int(file.readline().strip())
            except ValueError:
                print("Error: The first line of the file must be an integer representing the number of atoms.")
                return None
            n_atoms += 1
            #title = file.readline().strip()
            # print(title)
            atoms_list = []
            
            for _ in range(n_atoms):
                line = file.readline().strip()
                #print(line)
                if not line:  # Skip empty lines
                    continue
                parts = line.split()
                if len(parts) < 7:  # Check if the line has enough data
                    #print(f"Warning: Skipping line with insufficient data: {line}")
                    continue
                atoms = {
                    'atom_num': int(parts[0]),
                    'atom_sym': parts[1],
                    'x': float(parts[2]),
                    'y': float(parts[3]),
                    'z': float(parts[4]),
                    'atom_type': int(parts[5]),
                    'connect': [int(num) for num in parts[6:]]                
                }
                atoms_list.append(atoms)
            #print(atoms_list)
            return atoms_list
    except FileNotFoundError:
        print(f"Error: The file {arc_file} was not found.")
        return None

def atoms_to_residues(atoms_list):
    residues = []
    current_residue = []
    
    for atom in atoms_list:
        current_residue.append(atom)
        # Assuming a new residue starts when the atom_sym is CA after N
        if len(current_residue) >= 3 and \
           current_residue[-3]['atom_sym'] == 'N' and \
           current_residue[-2]['atom_sym'] == 'CA' and \
           current_residue[-1]['atom_sym'] == 'C':
            residues.append(current_residue[:-3])  # Save the previous residue
            current_residue = current_residue[-3:]  # Start a new residue with the last 3 atoms (N, CA, C)

    if current_residue:
        residues.append(current_residue)  # Append the last residue

    #print(residues)
    
   
    return residues

def count_frames_in_arc_file(arc_file, line_to_search):
    """
    Counts how many times a specific line is repeated in a file.

    Args:
        arc_file: The path to the file.
        line_to_search (str): The line to search for and count.

    Returns:
        int: The number of times the line appears in the file.
    """ 
    count = 0
    try:
        with open(arc_file, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip() == line_to_search:  # Compare stripped lines to avoid whitespace issues
                    count += 1
        return count
    except FileNotFoundError:
        print(f"Error: The file {arc_file} was not found.")
        return None



def call_archive_ref(residues):
    """
    Asks the user for the paths to the parameter file, the arc file and the reference residue.
    """
    
    if residues:
            while True:
                try:
                    residue_index = int(input(f"Enter the index of the residue you want to use as a reference of EDA (1 - {len(residues) - 1}): "))
                    if 1 <= residue_index < len(residues):
                        break
                    else:
                        print("Invalid index. Please enter a valid index.")
                except ValueError:
                    print("Invalid input. Please enter an integer.")

            selected_residue = residues[residue_index]
            first_atom_num = selected_residue[0]['atom_num']
            last_atom_num = selected_residue[-1]['atom_num']
            print(f"Residue {residue_index} atom_num range: {first_atom_num} - {last_atom_num}")
    
    # Call TINKER archive command here
    # Example command:
    # TINKER execution command
    command = "archive"
    input_sequence = f"{arc_file}\n3\n-1 {first_atom_num - 1} 1, -{last_atom_num + 1} {line_to_search} 1\n1 {repetitions} 1\n"

    try:
        # Execute the command with subprocess.Popen, providing the input sequence
        process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate(input=input_sequence)

        # Print the output and error messages from the TINKER command
        print("TINKER Output:\n", stdout)
        if stderr:
            print("TINKER Error:\n", stderr)

    except FileNotFoundError:
        print(f"Error: The command 'archive' was not found.  Make sure TINKER is in your PATH.")
    except Exception as e:
        print(f"An error occurred: {e}")

#filepath = './test.arc'
param_file = input("Enter the path to the TINKER parameter file: ")
arc_file = input("Enter the path to the TINKER arc file: ")

atoms_list = read_tinker_xyz(arc_file)

try:
    with open(arc_file, 'r', encoding='utf-8') as file:
        line_to_search = file.readline().strip()  # Read the first line and strip whitespace
except FileNotFoundError:
    print(f"Error: The file {arc_file} was not found.")
    line_to_search = None  # Handle the case where the file is not found
except Exception as e:
    print(f"An error occurred while reading the file: {e}")
    line_to_search = None

if line_to_search:
    print(f"Searching for repetitions of the line: '{line_to_search}'")
else:
    print("Could not determine the line to search for.")
    exit()
repetitions = count_frames_in_arc_file(arc_file, line_to_search)

if repetitions is not None:
    print(f"The line '{line_to_search}' repeats {repetitions} times in the file.")

residues = atoms_to_residues(atoms_list)
if atoms_list is None:
    print("Error reading the TINKER XYZ file.")
    exit()      

call_archive_ref(residues)
