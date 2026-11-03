# Cheminformatics Virtual Laboratory

A Streamlit-based cheminformatics project for exploring molecular
structures from **SMILES** notation. The supplied Python chemistry
engine uses **RDKit** to parse molecular structures, calculate molecular
descriptors, generate 2D and 3D molecular representations, and create
PDF analysis reports.

The project assets supplied with this README include the
chemistry/reporting module, Python dependency lists, system package
list, and SRM Institute of Science and Technology logo.

## Features

The supplied `chem_core.py` module provides the following functionality:

-   **SMILES parsing and validation** using RDKit.
-   **2D molecular structure images**.
-   **3D conformer generation**, with hydrogen atoms added and geometry
    optimization attempted using MMFF (with UFF as a fallback).
-   **Molecular descriptor calculations**, including:
    -   Molecular formula
    -   Molecular weight and exact molecular weight
    -   LogP and topological polar surface area (TPSA)
    -   Hydrogen-bond donors and acceptors
    -   Rotatable bonds
    -   Ring, aromatic-ring, and aliphatic-ring counts
    -   Atom and bond counts, including calculated sigma and pi bond
        information
    -   Fraction Csp3 and molar refractivity
-   **Student-friendly property interpretations** and summary points.
-   **PDF report generation** for an individual molecule or a collection
    of molecules.

## Project files

``` text
project/
├── app.py                 # Streamlit user-interface entry point (not included in supplied files)
├── chem_core.py           # Chemistry calculations, molecular structures and PDF reports
├── requirements.txt       # Python dependencies
├── packages.txt           # System packages
├── srm_logo.jpeg          # SRM Institute of Science and Technology logo
└── README.md              # Project documentation
```

> **Important:** The supplied files do not include the Streamlit
> UI/entry-point script. Add the project's actual UI file (often named
> `app.py`) before trying to launch the complete application. The
> command below assumes that the entry-point file is named `app.py`.

## Requirements

-   Python 3.10 or a compatible Python version supported by the
    installed RDKit release.
-   The Python packages listed in `requirements.txt`.
-   The system libraries listed in `packages.txt` on Linux-based
    deployment environments.

### Python dependencies

The supplied `requirements.txt` lists:

-   `streamlit>=1.41`
-   `pandas`
-   `matplotlib`
-   `rdkit`
-   `reportlab`

### System packages

The supplied `packages.txt` lists:

-   `libxrender1`
-   `libxext6`
-   `libsm6`

## Installation and setup

### 1. Clone or copy the project

Place the project files in the same folder. Ensure the Streamlit UI
entry-point script is also present.

### 2. Create and activate a virtual environment

**Windows (PowerShell):**

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Linux system packages (if needed)

On Debian/Ubuntu-based systems:

``` bash
sudo apt-get update
sudo apt-get install -y libxrender1 libxext6 libsm6
```

These are system-level packages, not Python packages. They are listed
separately in `packages.txt`.

## Run the application

After adding the Streamlit UI entry-point file, run:

``` bash
streamlit run app.py
```

If your UI file has a different name, replace `app.py` with that
filename.

Streamlit will print a local address in the terminal, usually:

``` text
http://localhost:8501
```

Open that address in a web browser.

## Chemistry engine usage

`chem_core.py` contains reusable functions for the molecular workflow.
Its main functions include:

  ------------------------------------------------------------------------
  Function                             Purpose
  ------------------------------------ -----------------------------------
  `get_molecule(smiles)`               Parses a SMILES string into an
                                       RDKit molecule.

  `generate_2d_image(mol)`             Creates a 2D molecular image.

  `calculate_bond_information(mol)`    Calculates heavy-atom, sigma, pi,
                                       and total bond information.

  `calculate_properties(mol)`          Calculates the molecular
                                       descriptors.

  `generate_3d_molecule(mol)`          Generates and optimizes a 3D
                                       molecular conformer.

  `generate_molecule_pdf(...)`         Creates a basic
                                       molecular-properties PDF.

  `generate_final_report(...)`         Creates a detailed student
                                       molecular-analysis PDF.

  `generate_multi_final_report(...)`   Creates a combined report for
                                       multiple molecules.
  ------------------------------------------------------------------------

### Example: calculate properties from SMILES

``` python
from chem_core import get_molecule, calculate_properties

smiles = "CCO"  # Ethanol
molecule = get_molecule(smiles)

if molecule is None:
    print("Invalid SMILES notation.")
else:
    properties = calculate_properties(molecule)
    for name, value in properties.items():
        print(f"{name}: {value}")
```

## Reports and interpretation

The detailed report functions can include student information, the
submitted and canonical SMILES, molecular formula, 2D and generated 3D
structures, calculated properties, explanations, and learning notes.

The reported descriptors are computational results derived from the
submitted molecular structure. They are useful for learning and
molecular comparison, but they should not be treated as experimental
measurements or as a substitute for laboratory validation.

## Troubleshooting

-   **`ModuleNotFoundError`:** Activate the intended virtual environment
    and install dependencies using `pip install -r requirements.txt`.
-   **RDKit installation issues:** Check that your Python version and
    platform are supported by the RDKit package version available to
    pip.
-   **Missing shared-library errors on Linux:** Install the system
    packages listed in `packages.txt`.
-   **`streamlit run app.py` cannot find the file:** The UI entry-point
    file is not among the supplied files. Add it or use the actual
    filename in the command.
-   **Invalid molecular input:** Check that the input is valid SMILES
    notation. `get_molecule()` returns `None` when parsing fails.

## Acknowledgement

The supplied image asset is the SRM Institute of Science and Technology
logo. Use it in project materials only where you have permission to do
so.

------------------------------------------------------------------------

**Project:** Cheminformatics Virtual Laboratory\
**Core module:** `chem_core.py`
