import io
import os

import pandas as pd
import streamlit as st
import py3Dmol
from rdkit import Chem

from chem_core import (
    calculate_properties,
    generate_2d_image,
    generate_3d_molecule,
    generate_final_report,
    generate_multi_final_report,
    get_molecule,
)

st.set_page_config(
    page_title="Cheminformatics Virtual Laboratory",
    page_icon="🧪",
    layout="wide",
)

PRIMARY = "#17365D"

# ---------- Header ----------
logo_path = "srm_logo.jpeg"
header_left, header_right = st.columns([1, 5])

with header_left:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

with header_right:
    st.title("Cheminformatics Virtual Laboratory")
    st.caption("Explore molecular structures, calculate chemical descriptors, and generate analysis reports.")

st.divider()

# ---------- Sidebar: student details ----------
st.sidebar.header("Student Information")
student_name = st.sidebar.text_input("Student name")
registration_number = st.sidebar.text_input("Registration number")
st.sidebar.info("Enter your details if you want them included in the PDF report.")

# ---------- SMILES input ----------
st.subheader("1. Enter Molecular Structure")
st.write(
    "Enter one SMILES string, or enter multiple SMILES strings on separate lines. "
    "Example: `CCO` represents ethanol."
)

smiles_text = st.text_area(
    "SMILES input",
    value="CCO",
    height=120,
    placeholder="Enter one SMILES string per line...",
)

analyze = st.button("Analyze molecule(s)", type="primary", use_container_width=True)

if analyze:
    input_smiles_list = [
        line.strip()
        for line in smiles_text.splitlines()
        if line.strip()
    ]

    if not input_smiles_list:
        st.error("Please enter at least one SMILES string.")
        st.stop()

    records = []
    invalid_smiles = []

    for smiles in input_smiles_list:
        molecule = get_molecule(smiles)
        if molecule is None:
            invalid_smiles.append(smiles)
            continue

        properties = calculate_properties(molecule)
        records.append((smiles, molecule, properties))

    st.session_state["molecule_records"] = records
    st.session_state["invalid_smiles"] = invalid_smiles
    st.session_state["student_name"] = student_name
    st.session_state["registration_number"] = registration_number

# ---------- Results ----------
records = st.session_state.get("molecule_records", [])
invalid_smiles = st.session_state.get("invalid_smiles", [])

if invalid_smiles:
    st.warning("These entries could not be read as valid SMILES: " + ", ".join(invalid_smiles))

if records:
    st.divider()
    st.subheader("2. Molecular Analysis")

    for index, (smiles, molecule, properties) in enumerate(records, start=1):
        with st.expander(f"Molecule {index} — {properties['Molecular Formula']}", expanded=(index == 1)):
            st.markdown(f"**Input SMILES:** `{smiles}`")
            st.markdown(f"**Canonical SMILES:** `{Chem.MolToSmiles(molecule)}`")

            tab_2d, tab_3d, tab_properties = st.tabs(
                ["2D Structure", "3D Structure", "Molecular Properties"]
            )

            with tab_2d:
                st.image(generate_2d_image(molecule), caption="2D molecular structure", use_container_width=True)

            with tab_3d:
                molecule_3d = generate_3d_molecule(molecule)
                if molecule_3d is None:
                    st.warning("A 3D conformer could not be generated for this molecule.")
                else:
                    mol_block = Chem.MolToMolBlock(molecule_3d)
                    viewer = py3Dmol.view(width=850, height=480)
                    viewer.addModel(mol_block, "mol")
                    viewer.setStyle({"stick": {}, "sphere": {"scale": 0.25}})
                    viewer.setBackgroundColor("white")
                    viewer.zoomTo()
                    st.components.v1.html(viewer._make_html(), height=500, scrolling=False)

            with tab_properties:
                property_df = pd.DataFrame(
                    list(properties.items()),
                    columns=["Property", "Value"],
                )
                st.dataframe(property_df, use_container_width=True, hide_index=True)

    # ---------- Downloads ----------
    st.divider()
    st.subheader("3. Download Your Results")

    download_left, download_right = st.columns(2)

    with download_left:
        if len(records) == 1:
            smiles, molecule, properties = records[0]
            pdf_data = generate_final_report(
                st.session_state.get("student_name", ""),
                st.session_state.get("registration_number", ""),
                smiles,
                molecule,
                properties,
            )
            pdf_name = "molecular_analysis_report.pdf"
        else:
            pdf_data = generate_multi_final_report(
                st.session_state.get("student_name", ""),
                st.session_state.get("registration_number", ""),
                records,
            )
            pdf_name = "multi_molecule_analysis_report.pdf"

        st.download_button(
            "Download PDF report",
            data=pdf_data,
            file_name=pdf_name,
            mime="application/pdf",
            use_container_width=True,
        )

    with download_right:
        csv_rows = []
        for index, (smiles, molecule, properties) in enumerate(records, start=1):
            row = {
                "Molecule": index,
                "Input SMILES": smiles,
                "Canonical SMILES": Chem.MolToSmiles(molecule),
                **properties,
            }
            csv_rows.append(row)

        csv_buffer = io.StringIO()
        pd.DataFrame(csv_rows).to_csv(csv_buffer, index=False)

        st.download_button(
            "Download CSV data",
            data=csv_buffer.getvalue(),
            file_name="molecular_properties.csv",
            mime="text/csv",
            use_container_width=True,
        )

else:
    st.info("Enter a SMILES string above and select **Analyze molecule(s)** to see the results.")

# ---------- Footer ----------
st.divider()
st.caption("Educational tool: calculated molecular descriptors are computational estimates and should be interpreted alongside experimental data.")
