"""
Gaussian 09 Output File Analyzer

This script analyzes Gaussian 09 output files and extracts relevant quantum chemical calculation
data into organized text files. It handles various types of calculations including:
- Geometry optimizations
- Frequency calculations
- Single-point energy calculations
- Electronic structure analysis

The analyzer extracts and processes:
1. SCF Energies: Self-consistent field energies in Hartrees, showing convergence and final energy
2. Optimized Geometries: Cartesian coordinates of atoms in the optimized structure
3. Vibrational Frequencies: Normal modes and their frequencies, useful for:
   - Confirming minimum energy structures (no negative frequencies)
   - Identifying transition states (exactly one negative frequency)
   - Zero-point energy corrections
4. Electronic Structure: Information about molecular orbitals and electron configuration

All data is saved in human-readable text files with timestamps for tracking calculation history.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
import datetime

class GaussianAnalyzer:
    def __init__(self, filename: str):
        """Initialize the analyzer with a Gaussian output file.
        
        Args:
            filename (str): Path to the Gaussian 09 output file
            
        The data dictionary stores:
            energies: List of SCF energies from each optimization step
            geometries: List of molecular geometries during optimization
                       Each geometry is a list of dictionaries with atomic numbers and coordinates
            frequency_profiles: List of frequency profiles, each a list of vibrational frequencies in cm^-1
            electronic_structure: Dictionary containing:
                - Electronic state information
                - Occupied and virtual orbital eigenvalues
                - HOMO-LUMO information
            calculation_info: Dictionary containing:
                - Route section (calculation parameters)
                - Basis set information
                - Method details
        """
        self.filename = filename
        self.data = {
            'energies': [],
            'geometries': [],
            'frequency_profiles': [],
            'electronic_structure': {},
            'calculation_info': {}
        }
        
    def read_file(self) -> None:
        """Read and process the Gaussian output file."""
        with open(self.filename, 'r') as f:
            content = f.readlines()
            
        self._extract_calculation_info(content)
        self._extract_energies(content)
        self._extract_geometries(content)
        self._extract_frequencies(content)
        self._extract_electronic_structure(content)
    
    def _extract_calculation_info(self, content: List[str]) -> None:
        """Extract basic calculation information from the Gaussian output file.
        
        Processes the route section which contains:
        - Calculation type (Opt, Freq, SP, etc.)
        - Theory level (HF, DFT, MP2, etc.)
        - Basis set information
        - Additional keywords and parameters
        
        This information is crucial for understanding the type and quality of the calculation."""
        for i, line in enumerate(content):
            if "Route" in line:
                route_section = []
                j = i + 1
                while j < len(content) and content[j].strip():
                    route_section.append(content[j].strip())
                    j += 1
                self.data['calculation_info']['route'] = ' '.join(route_section)
                break

    def _extract_energies(self, content: List[str]) -> None:
        """Extract various energy values from the calculation.
        
        Finds and stores:
        - SCF (Self-Consistent Field) energies in Hartrees
        - Energy evolution during geometry optimization
        - Final converged energy
        
        The SCF energy represents the electronic energy of the system at each geometry.
        For optimization calculations, multiple energies show the convergence process.
        The final energy is used for thermochemistry and relative energy calculations."""
        scf_pattern = r"SCF Done:.*=\s*(-?\d+\.\d+)"
        for line in content:
            if "SCF Done" in line:
                match = re.search(scf_pattern, line)
                if match:
                    self.data['energies'].append(float(match.group(1)))

    def _extract_geometries(self, content: List[str]) -> None:
        """Extract molecular geometries from the optimization process.
        
        Processes the "Standard orientation" sections which contain:
        - Atomic numbers (nuclear charge)
        - Cartesian coordinates (X, Y, Z) in Angstroms
        - Geometry at each optimization step
        
        The geometries show the molecular structure evolution during optimization.
        The final geometry represents the optimized molecular structure.
        Multiple geometries are stored to track structural changes during optimization.
        
        Standard orientation is used (rather than input orientation) because it:
        - Places the center of nuclear charge at the origin
        - Aligns the principal axes with the Cartesian axes
        - Provides a standardized view of the molecule"""
        reading_geom = False
        current_geom = []
        
        for line in content:
            if "Standard orientation" in line:
                reading_geom = True
                current_geom = []
                continue
            
            if reading_geom:
                if "--------------------" in line:
                    continue
                if "Rotational constants" in line:
                    reading_geom = False
                    if current_geom:
                        self.data['geometries'].append(current_geom)
                    continue
                
                parts = line.split()
                if len(parts) == 6 and parts[0].isdigit():
                    current_geom.append({
                        'atomic_number': int(parts[1]),
                        'coordinates': [float(x) for x in parts[3:6]]
                    })

    def _extract_frequencies(self, content: List[str]) -> None:
        """Extract vibrational frequencies from frequency calculations.

        Organizes frequencies into separate profiles for each computed frequency calculation.
        Each profile contains the vibrational frequencies for that specific calculation.

        Vibrational frequencies are crucial for:
        1. Confirming the nature of stationary points:
           - Minimum energy structures: All frequencies are positive
           - Transition states: Exactly one negative frequency
           - Higher-order saddle points: Multiple negative frequencies

        2. Thermochemistry calculations:
           - Zero-point vibrational energy (ZPVE)
           - Thermal corrections to energy
           - Entropy contributions

        3. IR/Raman spectroscopy prediction:
           - Vibrational modes and their frequencies
           - IR intensities

        Frequencies are reported in cm^-1 (wavenumbers)."""
        current_profile = None

        for line in content:
            if "Harmonic frequencies" in line:
                if current_profile is not None:
                    self.data['frequency_profiles'].append(current_profile)
                current_profile = []
            elif "Frequencies --" in line and current_profile is not None:
                freqs = [float(x) for x in line.split("--")[1].split()]
                current_profile.extend(freqs)

        if current_profile is not None:
            self.data['frequency_profiles'].append(current_profile)

    def _extract_electronic_structure(self, content: List[str]) -> None:
        """Extract electronic structure information from the calculation.

        Processes and stores:
        1. Electronic State Information:
           - Multiplicity (singlet, doublet, etc.)
           - Total charge
           - Electronic configuration

        2. Molecular Orbital Information:
           - Orbital energies (eigenvalues) for occupied and virtual orbitals
           - Occupied vs. Virtual orbitals
           - HOMO (Highest Occupied Molecular Orbital) energy
           - LUMO (Lowest Unoccupied Molecular Orbital) energy

        This information is valuable for:
        - Understanding electronic excitations
        - Analyzing chemical reactivity
        - Calculating ionization potentials and electron affinities
        - Predicting UV-Vis spectra

        Eigenvalues are reported in Hartrees (atomic units)."""
        occ_pattern = r"Alpha\s+occ\.\s+eigenvalues\s+--\s+(.*)"
        virt_pattern = r"Alpha\s+virt\.\s+eigenvalues\s+--\s+(.*)"

        for i, line in enumerate(content):
            if "electronic state" in line.lower():
                self.data['electronic_structure']['state'] = line.strip()
            if "Alpha  occ. eigenvalues" in line:
                match = re.search(occ_pattern, line)
                if match:
                    eigenvalues = [float(x) for x in match.group(1).split()]
                    self.data['electronic_structure']['occupied_eigenvalues'] = eigenvalues
            if "Alpha virt. eigenvalues" in line:
                match = re.search(virt_pattern, line)
                if match:
                    virt_eigenvalues = [float(x) for x in match.group(1).split()]
                    self.data['electronic_structure']['virtual_eigenvalues'] = virt_eigenvalues

    def save_results(self, output_dir: str) -> None:
        """Save the extracted data to organized text files.
        
        Creates separate files for different types of data:
        1. *_energies_*.txt:
           - Lists all SCF energies
           - Shows energy convergence
           - Final optimized energy
        
        2. *_geometry_*.txt:
           - Final optimized geometry
           - Atomic numbers and coordinates
           - Standardized orientation
        
        3. *_frequencies_profile_{n}_*.txt:
            - Vibrational frequencies for each computed profile
            - Identifies any imaginary frequencies
            - Mode numbers and corresponding frequencies
            - Separate file for each frequency calculation profile
        
        4. *_summary_*.txt:
           - Calculation type and parameters
           - Final energy
           - Electronic structure information
           - Overall calculation summary
        
        Each file includes a timestamp to track calculation history.
        All energies are in Hartrees, coordinates in Angstroms,
        and frequencies in cm^-1 unless otherwise specified."""
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(self.filename))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save energies
        if self.data['energies']:
            energy_file = os.path.join(output_dir, f"{base_name}_energies_{timestamp}.txt")
            with open(energy_file, 'w') as f:
                f.write("SCF Energies (Hartree):\n")
                for i, energy in enumerate(self.data['energies'], 1):
                    f.write(f"Step {i}: {energy:.6f}\n")

        # Save final geometry
        if self.data['geometries']:
            geom_file = os.path.join(output_dir, f"{base_name}_geometry_{timestamp}.txt")
            with open(geom_file, 'w') as f:
                f.write("Final Optimized Geometry (Angstroms):\n")
                f.write("Atom    X           Y           Z\n")
                f.write("-" * 40 + "\n")
                for atom in self.data['geometries'][-1]:
                    coords = atom['coordinates']
                    f.write(f"{atom['atomic_number']:4d}  {coords[0]:10.6f} {coords[1]:10.6f} {coords[2]:10.6f}\n")

        # Save frequencies for each profile
        if self.data['frequency_profiles']:
            for profile_idx, profile in enumerate(self.data['frequency_profiles'], 1):
                freq_file = os.path.join(output_dir, f"{base_name}_frequencies_profile_{profile_idx}_{timestamp}.txt")
                with open(freq_file, 'w') as f:
                    f.write(f"Vibrational Frequencies Profile {profile_idx} (cm-1):\n")
                    for i, freq in enumerate(profile, 1):
                        f.write(f"Mode {i:3d}: {freq:10.2f}\n")

        # Save calculation summary
        summary_file = os.path.join(output_dir, f"{base_name}_summary_{timestamp}.txt")
        with open(summary_file, 'w') as f:
            f.write("Gaussian 09 Calculation Summary\n")
            f.write("=" * 50 + "\n\n")
            
            if 'route' in self.data['calculation_info']:
                f.write("Route Section:\n")
                f.write(self.data['calculation_info']['route'] + "\n\n")
            
            if self.data['energies']:
                f.write(f"Final Energy: {self.data['energies'][-1]:.6f} Hartree\n\n")
            
            if self.data['electronic_structure']:
                f.write("Electronic Structure Information:\n")
                for key, value in self.data['electronic_structure'].items():
                    f.write(f"{key}: {value}\n")

def process_gaussian_files(input_dir: str, output_dir: str) -> None:
    """Process all Gaussian output files in the specified directory.
    
    Args:
        input_dir (str): Directory containing Gaussian output files
                        Accepts files with extensions: .log, .out, .gaussian
        output_dir (str): Directory where analysis results will be saved
                         Will be created if it doesn't exist
    
    The function:
    1. Scans the input directory for Gaussian output files
    2. Creates a GaussianAnalyzer instance for each file
    3. Processes each file to extract all relevant chemical data
    4. Saves organized results in the output directory
    5. Handles errors gracefully and reports any processing issues
    
    Each file is processed independently, allowing for batch analysis
    of multiple calculations with different parameters or molecules."""
    for filename in os.listdir(input_dir):
        if filename.endswith(('.log', '.out', '.gaussian')):
            try:
                filepath = os.path.join(input_dir, filename)
                analyzer = GaussianAnalyzer(filepath)
                analyzer.read_file()
                analyzer.save_results(output_dir)
                print(f"Successfully processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_directory = os.path.dirname(os.path.abspath(__file__))  # Current directory
    output_directory = os.path.join(input_directory, "gaussian_analysis_results")
    
    print("Starting Gaussian output analysis...")
    process_gaussian_files(input_directory, output_directory)
    print("Analysis complete. Results saved in:", output_directory)
