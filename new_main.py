import subprocess
import os
import glob 
import time
import sys

def get_header_and_repetitions(arc_file):
    """Reads the header line and counts its repetitions (frames)."""
    global line_to_search
    global repetitions
    
    line_to_search = None
    repetitions = None
    try:
        with open(arc_file, 'r', encoding='utf-8') as file:
            line_to_search = file.readline().strip()
    except FileNotFoundError:
        print(f"Error: The file {arc_file} was not found.")
        return None, None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None, None

    if line_to_search:
        print(f"Header line found: '{line_to_search}'")
        #repetitions = count_frames_in_arc_file(arc_file, line_to_search)
        count = 0
        try:
            with open(arc_file, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip() == line_to_search:
                        count += 1
            repetitions = count
        except FileNotFoundError:
            print(f"Error: The file {arc_file} was not found.")
            return None, None
        if count is not None:
             print(f"The header line repeats {count} times (frames).")
        return line_to_search, count
    else:
        print("Could not determine the header line.")
        return None, None

def read_tinker_xyz(arc_file):
    """
    Reads a TINKER ARC file and returns a list of atoms.
    """
    try:
        with open (arc_file, 'r') as file:
            try:
                n_atoms = int(file.readline().strip())
            except ValueError:
                print("Error: The first line of the file must be an integer representing the number of atoms.")
                return None
            
            n_atoms += 1
            atoms_list = []
            
            for _ in range(n_atoms):
                line = file.readline().strip()
                #print(line)
                if not line:  # Skip empty lines
                    continue
                parts = line.split()
                if len(parts) < 7:  # Check if the line has enough data
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
                atoms['connect'] = [num for num in atoms['connect'] if num != 0]
                atoms_list.append(atoms)
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
            
            residues.append(current_residue[:-3]) # Save the previous residue
            current_residue = current_residue[-3:] # Start a new residue 

    if current_residue:
        residues.append(current_residue)  # Append the last residue
    
    return residues

def archive_sep_pair(residues,prm_file):
    """
    Separates all of the possible pairs of the protein.
    """
    
    if residues:
        n = len(residues)
        for i in range(1, n):
            for j in range(i + 1, n):
                res1 = residues[i]
                res2 = residues[j]
                
                #Residue 1 atoms numbers
                res1_an1 = res1[0]['atom_num']
                res1_an2 = res1[-1]['atom_num']
                
                #Residue 2 atoms numbers
                res2_an1 = res2[0]['atom_num']
                res2_an2 = res2[-1]['atom_num']
                
                # Determines the order of the pairs of residues
                if res1_an1 == 1 and res2_an1 == 17:
                    command = "archive"
                    input = f"{arc_file}\n3\n -{res2_an2 + 1} -{line_to_search} 0\n1 {repetitions} 1\n\r"
                elif res1_an2 + 1 == res2_an1:
                    command = "archive"
                    input = f"{arc_file}\n3\n-1 -{res1_an1 - 1} -{res2_an2 + 1} -{line_to_search} 0\n1 {repetitions} 1\n\r"
                elif res1_an1 < res2_an1:
                    command = "archive"
                    input = f"{arc_file}\n3\n-1 -{res1_an1 - 1} -{res1_an2 + 1} -{res2_an1 - 1} -{res2_an2 + 1} -{line_to_search} 1\n1 {repetitions} 1\n\r"
                else:
                    command = "archive"
                    input = f"{arc_file}\n3\n-1 -{res2_an1 - 1} -{res2_an2 + 1} -{res1_an1 - 1} -{res1_an2 + 1} -{line_to_search} 1\n1 {repetitions} 1\n\r"

                # Executes archive.x to separate the residues
                try:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout, stderr = process.communicate(input=input.encode())
                    print(f"--- TINKER Output ---\n",stdout)
                    if stderr:
                        print(f"TINKER Error:\n", stderr)
                except FileNotFoundError:
                    print(f"Error: archive did not run correctly.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                
                #Renames the output file for easier identification
                list_of_files = glob.glob('./EDA-test/*')
                newest_files = max(list_of_files, key=os.path.getctime)
                try:
                    os.rename(newest_files, f"pair_{i}_{j}.arc")
                    
                except FileNotFoundError:
                    print(f"Error: The file '{newest_files}' was not found for renaming.")
                except OSError as e:
                    print(f"Error: Could not rename the file. {e}")
                
                #Connectivity check and delete 0 in the connect list
                # Read the file and process each atom's connect list
                for file_name in glob.glob("pair_*.arc"):
                    try:
                        with open(file_name, 'r') as file:
                            lines = file.readlines()
                        
                        # Process each line (atom) in the file
                        for m in range(1, len(lines)):  # Skip header lines
                            parts = lines[m].split()
                            if len(parts) > 6:
                                connect_list = [int(num) for num in parts[6:]]
                                
                                # Remove 0 from the connect list
                                connect_list = [num for num in connect_list if num != 0]
                                
                                # Update the line with the modified connect list
                                lines[m] = ' '.join(parts[:6] + [str(num) for num in connect_list]) + '\n'
                        
                        # Write the modified content back to the file
                        with open(file_name, 'w') as file:
                            file.writelines(lines)
                            
                    except FileNotFoundError:
                        print(f"Error: The file '{file_name}' was not found.")
                    except Exception as e:
                        print(f"An error occurred while processing '{file_name}': {e}")
                        
                # Executes analyze.x process on the fly
                
                command = "analyze"
                a_res = f"pair_{i}_{j}.arc"
                input = f"{a_res}\n{prm_file}\nE\n\r"
                try:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                    stdout, stderr = process.communicate(input=input)
                    
                    if stderr:
                        print(f"TINKER Error:\n", stderr)
                    else:
                        # Parse the output
                        lines = stdout.splitlines()
                        energy_components = {}
                        for line in lines:
                            if "Intermolecular Energy :" in line:
                                energy_components["Intermolecular Energy"] = float(line.split()[3])
                            elif "Van der Waals" in line:
                                energy_components["Van der Waals"] = float(line.split()[3])
                            elif "Atomic Multipoles" in line:
                                energy_components["Atomic Multipoles"] = float(line.split()[2])
                            elif "Polarization " in line:
                                energy_components["Polarization"] = float(line.split()[1])
                        
                        # Store the energy components for later analysis
                        for component, value in energy_components.items():
                            if not hasattr(Main, 'all_energy_components'):
                                Main.all_energy_components = {}
                            if component not in Main.all_energy_components:
                                Main.all_energy_components[component] = []
                            Main.all_energy_components[component].append(value)
                            print(f"{component}: {value}")
                            
                        # Calculate and print the average and standard deviation for each energy component
                        if hasattr(Main, 'all_energy_components'):
                            # Prepare data for writing to the file
                            output_lines = []
                            
                            # Header
                            header_components = list(Main.all_energy_components.keys())
                            header_line = " ".join([f"{c:<15}" for c in header_components])  # Adjust spacing as needed
                            output_lines.append(f"{header_line}\n")
                            
                            # Sub-header
                            subheader_line = " ".join(["AVG STD".center(15) for _ in header_components])
                            output_lines.append(f"{subheader_line}\n")
                            
                            # Data line
                            data_line = f"res {i} - res {j} "
                            for component in header_components:
                                values = Main.all_energy_components[component]
                                avg = sum(values) / len(values)
                                std_dev = (sum([(x - avg) ** 2 for x in values]) / len(values)) ** 0.5
                                data_line += f"{avg:<7.2f} {std_dev:<7.2f} "
                            output_lines.append(data_line + "\n")
                            
                            # Write to file
                            with open("energy_analysis.txt", "a") as outfile:  # "a" for append mode
                                outfile.writelines(output_lines)
                            # Delete the pair_{i}_{j}.arc file
                
                except FileNotFoundError:
                    print(f"Error: analyze did not run correctly.")
                except Exception as e:
                    print(f"An error occurred: {e}")
                
                try:
                    os.remove(f"pair_{i}_{j}.arc")
                    print(f"File pair_{i}_{j}.arc deleted successfully.")
                except FileNotFoundError:
                    print(f"Error: File pair_{i}_{j}.arc not found.")
                except Exception as e:
                    print(f"Error deleting file pair_{i}_{j}.arc: {e}")

        
    else:
        print("No residues found to process.")
        return None

class Main:
    all_energy_components = {}
 
arc_file = "./EDA-test/test.arc"
prm_file = "./EDA-test/amoebabio18.prm"

get_header_and_repetitions(arc_file)
atoms_list = read_tinker_xyz(arc_file)
residues = atoms_to_residues(atoms_list)
archive_sep_pair(residues, prm_file)


