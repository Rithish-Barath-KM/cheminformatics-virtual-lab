import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import py3Dmol
import streamlit.components.v1 as components

from rdkit import Chem
from rdkit.Chem import Draw, Descriptors, rdMolDescriptors
from rdkit.Chem import AllChem
from io import BytesIO

from chem_core import (
    calculate_properties,
    generate_2d_image,
    generate_3d_molecule,
    generate_final_report,
    generate_multi_final_report,
    get_molecule,
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Cheminformatics Virtual Laboratory",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0b1120;
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

h1, h2, h3 {
    color: #60a5fa;
}

p, label {
    color: #cbd5e1;
}

.stButton > button {
    background-color: #2563eb;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}

.stButton > button:hover {
    background-color: #1d4ed8;
    color: white;
}

[data-testid="stMetric"] {
    background-color: #172554;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #1e40af;
}

[data-testid="stMetricValue"] {
    color: #60a5fa;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    "<h1 style='text-align:center;'>🧪 CHEMINFORMATICS VIRTUAL LAB</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;'>Explore molecules, calculate chemical properties and visualize molecular structures.</p>",
    unsafe_allow_html=True
)

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.title("🧪 Virtual Lab")

    st.caption("Student Laboratory Portal")

    st.divider()

    student_name = st.text_input(
        "Student Name",
        placeholder="Enter your name"
    )

    registration_number = st.text_input(
        "Registration Number",
        placeholder="Enter registration number"
    )

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Molecule Explorer",
            "Batch Analysis",
            "Compare Molecules",
            "Report Center",
            "About the Lab"
        ]
    )

    st.divider()

    st.caption("Cheminformatics Virtual Laboratory")
    st.caption("Educational Project")

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "molecule_data" not in st.session_state:
    st.session_state.molecule_data = []

if "current_molecule" not in st.session_state:
    st.session_state.current_molecule = None

if "current_smiles" not in st.session_state:
    st.session_state.current_smiles = ""
    # --------------------------------------------------
# OVERVIEW PAGE
# --------------------------------------------------

if page == "Overview":

    st.subheader("Welcome to the Virtual Laboratory")

    st.write(
        "A digital chemistry laboratory designed to explore "
        "molecular structures and chemical properties."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Laboratory", "Active")

    with col2:
        st.metric("Analysis Mode", "Molecular")

    with col3:
        st.metric(
            "Molecules Analysed",
            len(st.session_state.molecule_data)
        )

    st.divider()

    st.subheader("Laboratory Modules")

    c1, c2 = st.columns(2)

    with c1:
        st.info(
            "**Molecule Explorer**\n\n"
            "Enter a SMILES notation and explore its molecular structure."
        )

        st.info(
            "**Batch Analysis**\n\n"
            "Analyse multiple molecules together."
        )

    with c2:
        st.info(
            "**Compare Molecules**\n\n"
            "Compare chemical properties of different molecules."
        )

        st.info(
            "**Report Center**\n\n"
            "Access your molecular analysis reports."
        )


# --------------------------------------------------
# MOLECULE EXPLORER
# --------------------------------------------------

elif page == "Molecule Explorer":

    st.subheader("🔬 Molecule Explorer")

    st.write(
        "Enter a valid SMILES notation to analyse a molecule."
    )

    smiles = st.text_input(
        "Enter SMILES Notation",
        placeholder="Example: CCO"
    )

    if st.button("Analyse Molecule"):

        if not smiles.strip():

            st.warning("Please enter a SMILES notation.")

        else:

            mol = get_molecule(smiles.strip())

            if mol is None:

                st.error(
                    "Invalid SMILES notation. Please check your input."
                )

            else:

                st.session_state.current_molecule = mol
                st.session_state.current_smiles = smiles.strip()

                try:
                    properties = calculate_properties(mol)

                    st.session_state.molecule_data.append({
                        "SMILES": smiles.strip(),
                        "Properties": properties
                    })

                    st.success("Molecule analysed successfully!")

                except Exception as e:

                    st.error(f"Analysis error: {e}")

    # DISPLAY MOLECULE

    mol = st.session_state.current_molecule

    if mol is not None:

        st.divider()

        st.subheader("Molecular Structure")

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("#### 2D Structure")

            try:

                image = generate_2d_image(mol)

                st.image(
                    image,
                    caption="2D Molecular Structure",
                    use_container_width=True
                )

            except Exception as e:

                st.warning(f"2D visualization unavailable: {e}")

        with col2:

            st.markdown("#### 3D Structure")

            try:

                viewer = generate_3d_molecule(mol)

                if isinstance(viewer, str):

                    components.html(
                        viewer,
                        height=400,
                        scrolling=False
                    )

                else:

                    components.html(
                        viewer._make_html(),
                        height=400,
                        scrolling=False
                    )

            except Exception as e:

                st.warning(f"3D visualization unavailable: {e}")

        st.divider()

        st.subheader("Chemical Properties")

        try:

            properties = calculate_properties(mol)

            if isinstance(properties, dict):

                property_df = pd.DataFrame(
                    list(properties.items()),
                    columns=["Property", "Value"]
                )

                st.dataframe(
                    property_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.write(properties)

        except Exception as e:

            st.error(f"Unable to display properties: {e}")

        st.caption(
            f"SMILES: {st.session_state.current_smiles}"
        )
        # --------------------------------------------------
# BATCH ANALYSIS
# --------------------------------------------------

elif page == "Batch Analysis":

    st.subheader("📊 Batch Molecular Analysis")

    st.write("Analyse multiple molecules simultaneously.")

    batch_input = st.text_area(
        "Enter SMILES (one molecule per line)",
        placeholder="CCO\nCC\nO\nCC(=O)O",
        height=150
    )

    if st.button("Run Batch Analysis"):

        results = []

        for smiles in batch_input.splitlines():

            smiles = smiles.strip()

            if not smiles:
                continue

            try:
                mol = get_molecule(smiles)

                if mol is None:
                    continue

                properties = calculate_properties(mol)

                row = {"SMILES": smiles}

                if isinstance(properties, dict):
                    row.update(properties)

                results.append(row)

            except Exception:
                continue

        if results:

            batch_df = pd.DataFrame(results)

            st.session_state.batch_results = batch_df

            st.success(
                f"Successfully analysed {len(results)} molecules!"
            )

        else:
            st.error("No valid molecules found.")

    if "batch_results" in st.session_state:

        st.subheader("Batch Results")

        st.dataframe(
            st.session_state.batch_results,
            use_container_width=True,
            hide_index=True
        )

        csv = st.session_state.batch_results.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download CSV",
            csv,
            "batch_analysis.csv",
            "text/csv"
        )


# --------------------------------------------------
# COMPARE MOLECULES
# --------------------------------------------------

elif page == "Compare Molecules":

    st.subheader("⚖️ Compare Molecules")

    st.write(
        "Enter two SMILES notations to compare their properties."
    )

    col1, col2 = st.columns(2)

    with col1:
        smiles1 = st.text_input(
            "First Molecule",
            placeholder="CCO"
        )

    with col2:
        smiles2 = st.text_input(
            "Second Molecule",
            placeholder="CC(=O)O"
        )

    if st.button("Compare"):

        if not smiles1.strip() or not smiles2.strip():

            st.warning("Enter both SMILES notations.")

        else:

            mol1 = get_molecule(smiles1.strip())
            mol2 = get_molecule(smiles2.strip())

            if mol1 is None or mol2 is None:

                st.error("One or both SMILES notations are invalid.")

            else:

                try:

                    prop1 = calculate_properties(mol1)
                    prop2 = calculate_properties(mol2)

                    if isinstance(prop1, dict) and isinstance(prop2, dict):

                        comparison = pd.DataFrame({
                            "Property": list(prop1.keys()),
                            "Molecule 1": list(prop1.values()),
                            "Molecule 2": [
                                prop2.get(key, "N/A")
                                for key in prop1.keys()
                            ]
                        })

                        st.success("Comparison completed!")

                        st.dataframe(
                            comparison,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:
                        st.error("Property comparison is unavailable.")

                except Exception as e:

                    st.error(f"Comparison error: {e}")


# --------------------------------------------------
# REPORT CENTER
# --------------------------------------------------

elif page == "Report Center":

    st.subheader("📄 Report Center")

    st.write(
        "View and export your molecular analysis history."
    )

    if st.session_state.molecule_data:

        report_data = []

        for item in st.session_state.molecule_data:

            row = {"SMILES": item["SMILES"]}

            if isinstance(item["Properties"], dict):
                row.update(item["Properties"])

            report_data.append(row)

        report_df = pd.DataFrame(report_data)

        st.dataframe(
            report_df,
            use_container_width=True,
            hide_index=True
        )

        csv_data = report_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Analysis History",
            csv_data,
            "molecule_history.csv",
            "text/csv"
        )

    else:

        st.info(
            "No analysis history available. "
            "Analyse a molecule first."
        )


# --------------------------------------------------
# ABOUT THE LAB
# --------------------------------------------------

elif page == "About the Lab":

    st.subheader("🧪 About Cheminformatics Virtual Laboratory")

    st.write("""
    The Cheminformatics Virtual Laboratory is an educational
    application designed to explore molecular structures and
    understand chemical properties using computational tools.
    """)

    st.markdown("### Laboratory Features")

    st.markdown("""
    - Molecular SMILES input
    - 2D molecular visualization
    - 3D molecular visualization
    - Chemical property calculations
    - Batch molecular analysis
    - Molecule comparison
    - CSV report generation
    """)

    st.markdown("### Technologies Used")

    st.markdown("""
    - Python
    - Streamlit
    - RDKit
    - Pandas
    - Matplotlib
    - Py3Dmol
    """)

    st.divider()

    st.caption("Cheminformatics Virtual Laboratory")
    st.caption("Educational Project")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#64748b;">
        Cheminformatics Virtual Laboratory |
        Powered by Python and Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
