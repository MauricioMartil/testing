def read_tinker_xyz(filepath):
    try:
        with open (filepath, 'r') as file:
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
        print(f"Error: The file {filepath} was not found.")
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

def call_tinker_archive(residues):
    """
    Asks the user for the paths to the parameter file, the arc file and the reference residue.
    """
    param_file = input("Enter the path to the TINKER parameter file: ")
    arc_file = input("Enter the path to the TINKER arc file: ")

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
            #print(f"Residue {residue_index} atom_num range: {first_atom_num} - {last_atom_num}")
    
    try:
        with open (arc_file, 'r') as file:
            try:
                n_atoms = int(file.readline().strip())
                print(f"Number of atoms in the arc file: {n_atoms}")
                count = 0
                for line in file:
                    try:
                        frames = int(line.strip())
                        if frames == n_atoms:
                            count += 1
                    except ValueError:
                        break
                print(f"The first line repeats {count} times in the file.")
                file.seek(0)
            except ValueError:
                print("Error: The first line of the arc file must be an integer representing the number of atoms.")
                return None
    except FileNotFoundError:
        print(f"Error: The file {arc_file} was not found.")
        return None  
  
    # You can now use param_file_path and arc_file_path in your TINKER calculations.
    # For example, you might pass them as arguments to a subprocess call.
    #print(f"Parameter file path: {param_file}")
    #print(f"Arc file path: {arc_file}")

#/media/mauricio/Expansion/A3G/run/prod3/20/test.arc

    # TINKER execution.
    #command = f"archive {arc_file} 3 {first_atom_num} {last_atom_num}"

filepath = '/media/mauricio/Expansion/A3G/run/prod3/20/test.arc'
atoms_list = read_tinker_xyz(filepath)      
residues = atoms_to_residues(atoms_list)

call_tinker_archive(residues)
