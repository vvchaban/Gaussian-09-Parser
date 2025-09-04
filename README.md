# Gaussian Analyzer User Guide

## Overview

The Gaussian Analyzer is a Python script designed to analyze Gaussian 09 output files and extract key quantum chemical data. It processes various types of calculations including geometry optimizations, frequency calculations, and single-point energy calculations.

The analyzer extracts and organizes:
- SCF (Self-Consistent Field) energies
- Optimized molecular geometries
- Vibrational frequencies
- Electronic structure information

All extracted data is saved to timestamped text files for easy analysis and record-keeping.

## Requirements

- Python 3.6 or higher
- Gaussian 09 output files (.log, .out, or .gaussian extensions)
- No external dependencies required (uses only Python standard library)

## Installation

1. Download the `gaussian_analyzer.py` file
2. Ensure Python 3.6+ is installed on your system
3. Place the script in your desired working directory

## Usage

### Analyzing a Single File

To analyze a single Gaussian output file:

```python
from gaussian_analyzer import GaussianAnalyzer

# Initialize analyzer with file path
analyzer = GaussianAnalyzer('path/to/your/file.log')

# Read and process the file
analyzer.read_file()

# Save results to output directory
analyzer.save_results('output_directory')
```

### Batch Processing Multiple Files

To process all Gaussian output files in a directory:

```python
from gaussian_analyzer import process_gaussian_files

# Process all files in input directory
process_gaussian_files('input_directory', 'output_directory')
```

### Command Line Usage

Run the script directly from command line:

```bash
python gaussian_analyzer.py
```

This will process all Gaussian output files in the current directory and save results to `gaussian_analysis_results/`.

## Output Files

The analyzer creates several types of output files, each with a timestamp:

### Energy Files (`*_energies_*.txt`)
Contains SCF energies from each optimization step:
```
SCF Energies (Hartree):
Step 1: -56.789012
Step 2: -56.812345
...
```

### Geometry Files (`*_geometry_*.txt`)
Contains the final optimized geometry:
```
Final Optimized Geometry (Angstroms):
Atom    X           Y           Z
----------------------------------------
1     0.000000   0.000000   0.000000
6     1.234567   0.000000   0.000000
...
```

### Frequency Files (`*_frequencies_*.txt`)
Contains vibrational frequencies:
```
Vibrational Frequencies (cm-1):
Mode   1:    234.56
Mode   2:    345.67
...
```

### Summary Files (`*_summary_*.txt`)
Contains overall calculation information:
```
Gaussian 09 Calculation Summary
==================================================

Route Section:
# opt freq b3lyp/6-31g(d) geom=connectivity

Final Energy: -56.812345 Hartree

Electronic Structure Information:
...
```

## Examples

### Example 1: Basic Usage

```python
from gaussian_analyzer import GaussianAnalyzer

# Analyze a geometry optimization file
analyzer = GaussianAnalyzer('water_opt.log')
analyzer.read_file()
analyzer.save_results('./results')
```

### Example 2: Batch Processing

```python
from gaussian_analyzer import process_gaussian_files

# Process all files in the 'calculations' directory
process_gaussian_files('./calculations', './analysis_results')
```

### Example 3: Custom Output Directory

```python
import os
from gaussian_analyzer import GaussianAnalyzer

# Create custom output directory
output_dir = './my_analysis'
os.makedirs(output_dir, exist_ok=True)

analyzer = GaussianAnalyzer('molecule.log')
analyzer.read_file()
analyzer.save_results(output_dir)
```

## Troubleshooting

### Common Issues

1. **File not found error**
   - Ensure the file path is correct
   - Check file permissions
   - Verify the file exists

2. **No data extracted**
   - Check if the Gaussian output file is complete
   - Ensure the calculation finished successfully
   - Verify the file contains the expected calculation type

3. **Permission errors**
   - Ensure write permissions for the output directory
   - Check if the output directory is not read-only

4. **Memory issues with large files**
   - The script reads the entire file into memory
   - For very large output files, consider splitting them or using more memory

### Error Messages

- "Error processing [filename]: [error message]" - Check the specific error and file format
- "No SCF energies found" - The file may not contain energy calculations
- "No geometries found" - The file may not contain geometry optimization

## API Reference

### GaussianAnalyzer Class

#### `__init__(filename: str)`
Initialize the analyzer with a Gaussian output file path.

#### `read_file() -> None`
Read and process the Gaussian output file, extracting all available data.

#### `save_results(output_dir: str) -> None`
Save extracted data to organized text files in the specified directory.

### Functions

#### `process_gaussian_files(input_dir: str, output_dir: str) -> None`
Process all Gaussian output files in the input directory and save results to the output directory.

## File Formats

The analyzer recognizes Gaussian output files with the following extensions:
- `.log` - Standard Gaussian log files
- `.out` - Alternative output format
- `.gaussian` - Generic Gaussian output files

## Data Units

- Energies: Hartrees (atomic units)
- Coordinates: Angstroms
- Frequencies: cm⁻¹ (wavenumbers)
- Atomic numbers: Integer values corresponding to elements

## Tips

1. Always check that your Gaussian calculations completed successfully before analysis
2. Use descriptive filenames for your output files to maintain organization
3. The timestamped output files help track different analysis runs
4. For large datasets, consider processing files in batches
5. Review the summary files first to get an overview of each calculation

## Support

For issues or questions about the Gaussian Analyzer:
1. Check this user guide for common solutions
2. Verify your Gaussian output files are properly formatted
3. Ensure Python and file paths are correctly configured
