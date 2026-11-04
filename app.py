# ==================================================
# CHEMINFORMATICS VIRTUAL LABORATORY  —  app.py
# ==================================================

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from io import BytesIO

try:
    from rdkit import Chem
    from rdkit.Chem import Draw
    RDKIT_AVAILABLE = True
except Exception as _e:
    RDKIT_AVAILABLE = False
    RDKIT_ERROR = str(_e)

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
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root {
    --bg:        #0b1120;
    --panel:     #111827;
    --panel-2:   #172554;
    --border:    #1e40af;
    --accent:    #2563eb;
    --accent-h:  #1d4ed8;
    --text:      #e2e8f0;
    --muted:     #94a3b8;
    --success:   #22c55e;
    --danger:    #ef4444;
}

.stApp { background-color: var(--bg); color: var(--text); }

[data-testid="stSidebar"] { background-color: var(--panel); }

h1, h2, h3, h4 { color: #60a5fa; }
p, label, span { color: #cbd5e1; }

.stTextInput > div > div > input,
.stTextArea > div > textarea {
    background-color: #0f172a !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

.stButton > button,
.stDownloadButton > button {
    background-color: var(--accent);
    color: #fff;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
    font-weight: 600;
    transition: all .15s ease;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    background-color: var(--accent-h);
    transform: translateY(-1px);
}

[data-testid="stMetric"] {
    background-color: var(--panel-2);
    padding: 16px;
    border-radius: 12px;
    border: 1px solid var(--border);
}
[data-testid="stMetricValue"] { color: #60a5fa; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #cbd5e1; }

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stAlert"] {
    border-radius: 10px;
}

.lab-card {
    background: #0f172a;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 18px 20px;
    margin-bottom: 14px;
}
.lab-card h4 { margin: 0 0 6px 0; color: #93c5fd; }
.lab-card p  { margin: 0; color: #cbd5e1; font-size: 0.95rem; }

.hero {
    background: linear-gradient(135deg,#1e3a8a 0%,#0b1120 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px 24px;
    margin-bottom: 22px;
    text-align: center;
}
.hero h1 { margin: 0; font-size: 2.1rem; letter-spacing: .5px; }
.hero p  { margin: 8px 0 0 0; color: #cbd5e1; }

.footer {
    text-align: center;
    color: var(--muted);
    padding: 18px 0 8px 0;
    font-size: 0.9rem;
    border-top: 1px solid var(--border);
    margin-top: 30px;
}
</style>
""",
    unsafe_allow_html=True,
)

DEFAULTS = {
    "molecule_data": [],
    "current_molecule": None,
    "current_smiles": "",
    "current_properties": None,
    "batch_results": None,
    "student_name": "",
    "registration_number": "",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


def _add_to_history(smiles: str, properties: dict) -> None:
    existing = {row["SMILES"] for row in st.session_state.molecule_data}
    if smiles not in existing:
        st.session_state.molecule_data.append(
            {"SMILES": smiles, "Properties": properties}
        )


st.markdown(
    """
<div class="hero">
    <h1>🧪 CHEMINFORMATICS VIRTUAL LAB</h1>
    <p>Explore molecules, calculate chemical properties and visualise molecular structures.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("🧪 Virtual Lab")
    st.caption("Student Laboratory Portal")
    st.divider()

    st.session_state.student_name = st.text_input(
        "Student Name",
        value=st.session_state.student_name,
        placeholder="Enter your name",
    )
    st.session_state.registration_number = st.text_input(
        "Registration Number",
        value=st.session_state.registration_number,
        placeholder="Enter registration number",
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
            "About the Lab",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if st.session_state.student_name:
        st.success(f"👤 {st.session_state.student_name}")
    else:
        st.info("👤 Not signed in")

    st.caption(f"🔬 Analysed: **{len(st.session_state.molecule_data)}**")
    st.divider()
    st.caption("Cheminformatics Virtual Laboratory")
    st.caption("Educational Project")

if not RDKIT_AVAILABLE:
    st.error(
        "RDKit could not be imported. Please ensure `rdkit` is listed in "
        "`requirements.txt` and re-deploy.\n\n"
        f"Details: {RDKIT_ERROR}"
    )
    st.stop()


if page == "Overview":
    st.subheader("Welcome to the Virtual Laboratory")
    st.write(
        "A digital chemistry laboratory designed to explore "
        "molecular structures and chemical properties."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Laboratory", "Active")
    with c2:
        st.metric("Analysis Mode", "Molecular")
    with c3:
        st.metric("Molecules Analysed", len(st.session_state.molecule_data))

    st.divider()
    st.subheader("Laboratory Modules")

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            '<div class="lab-card"><h4>🔬 Molecule Explorer</h4>'
            "<p>Enter a SMILES notation and explore its molecular structure.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="lab-card"><h4>⚖️ Compare Molecules</h4>'
            "<p>Compare chemical properties of different molecules side-by-side.</p></div>",
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            '<div class="lab-card"><h4>📊 Batch Analysis</h4>'
            "<p>Analyse multiple molecules together and export CSV.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="lab-card"><h4>📄 Report Center</h4>'
            "<p>Access and download your complete molecular analysis history.</p></div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.subheader("Quick Start — Try a Sample")
    samples = {
        "Ethanol (CCO)": "CCO",
        "Acetic Acid (CC(=O)O)": "CC(=O)O",
        "Benzene (c1ccccc1)": "c1ccccc1",
        "Caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
        "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    }
    cols = st.columns(len(samples))
    for col, (label, smi) in zip(cols, samples.items()):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.current_smiles = smi
                mol = get_molecule(smi)
                if mol is not None:
                    st.session_state.current_molecule = mol
                    st.session_state.current_properties = calculate_properties(mol)
                    _add_to_history(smi, st.session_state.current_properties)
                    st.session_state["_nav_to"] = "Molecule Explorer"


elif page == "Molecule Explorer":
    st.subheader("🔬 Molecule Explorer")
    st.write("Enter a valid SMILES notation to analyse a molecule.")

    smiles_input = st.text_input(
        "Enter SMILES Notation",
        value=st.session_state.current_smiles,
        placeholder="Example: CCO",
    )

    col_a, col_b = st.columns([1, 1])
    with col_a:
        analyse = st.button("Analyse Molecule", use_container_width=True)
    with col_b:
        clear = st.button("Clear", use_container_width=True)

    if clear:
        st.session_state.current_molecule = None
        st.session_state.current_smiles = ""
        st.session_state.current_properties = None
        st.rerun()

    if analyse:
        if not smiles_input.strip():
            st.warning("Please enter a SMILES notation.")
        else:
            mol = get_molecule(smiles_input.strip())
            if mol is None:
                st.error("Invalid SMILES notation. Please check your input.")
            else:
                st.session_state.current_molecule = mol
                st.session_state.current_smiles = smiles_input.strip()
                try:
                    st.session_state.current_properties = calculate_properties(mol)
                    _add_to_history(
                        smiles_input.strip(),
                        st.session_state.current_properties,
                    )
                    st.success("Molecule analysed successfully!")
                except Exception as e:
                    st.error(f"Analysis error: {e}")

    mol = st.session_state.current_molecule
    if mol is not None:
        st.divider()
        st.subheader("Molecular Structure")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 2D Structure")
            try:
                image = generate_2d_image(mol)
                st.image(image, caption="2D Molecular Structure", use_container_width=True)
            except Exception as e:
                st.warning(f"2D visualisation unavailable: {e}")

        with col2:
            st.markdown("#### 3D Structure")
            try:
                viewer = generate_3d_molecule(mol)
                if isinstance(viewer, str):
                    html = viewer
                elif hasattr(viewer, "_make_html"):
                    html = viewer._make_html()
                elif hasattr(viewer, "get_html"):
                    html = viewer.get_html()
                else:
                    html = str(viewer)
                components.html(html, height=420, scrolling=False)
            except Exception as e:
                st.warning(f"3D visualisation unavailable: {e}")

        st.divider()
        st.subheader("Chemical Properties")

        properties = st.session_state.current_properties
        if properties is None:
            try:
                properties = calculate_properties(mol)
            except Exception as e:
                properties = None
                st.error(f"Unable to display properties: {e}")

        if isinstance(properties, dict) and properties:
            property_df = pd.DataFrame(
                list(properties.items()), columns=["Property", "Value"]
            )
            st.dataframe(property_df, use_container_width=True, hide_index=True)
        elif properties is not None:
            st.write(properties)

        st.caption(f"SMILES: `{st.session_state.current_smiles}`")


elif page == "Batch Analysis":
    st.subheader("📊 Batch Molecular Analysis")
    st.write("Analyse multiple molecules simultaneously.")

    batch_input = st.text_area(
        "Enter SMILES (one molecule per line)",
        placeholder="CCO\nCC\nO\nCC(=O)O",
        height=160,
    )

    if st.button("Run Batch Analysis", use_container_width=True):
        results = []
        failed = []

        for raw in batch_input.splitlines():
            smiles = raw.strip()
            if not smiles:
                continue
            try:
                mol = get_molecule(smiles)
                if mol is None:
                    failed.append(smiles)
                    continue
                properties = calculate_properties(mol)
                row = {"SMILES": smiles}
                if isinstance(properties, dict):
                    row.update(properties)
                results.append(row)
            except Exception:
                failed.append(smiles)

        if results:
            st.session_state.batch_results = pd.DataFrame(results)
            st.success(f"Successfully analysed **{len(results)}** molecule(s)!")
        else:
            st.error("No valid molecules found.")

        if failed:
            with st.expander(f"⚠️ {len(failed)} input(s) could not be analysed"):
                st.code("\n".join(failed))

    if st.session_state.batch_results is not None:
        st.subheader("Batch Results")
        st.dataframe(
            st.session_state.batch_results,
            use_container_width=True,
            hide_index=True,
        )

        csv = st.session_state.batch_results.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV",
            csv,
            "batch_analysis.csv",
            "text/csv",
            use_container_width=True,
        )


elif page == "Compare Molecules":
    st.subheader("⚖️ Compare Molecules")
    st.write("Enter two SMILES notations to compare their properties.")

    col1, col2 = st.columns(2)
    with col1:
        smiles1 = st.text_input("First Molecule", placeholder="CCO")
    with col2:
        smiles2 = st.text_input("Second Molecule", placeholder="CC(=O)O")

    if st.button("Compare", use_container_width=True):
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
                        comparison = pd.DataFrame(
                            {
                                "Property": list(prop1.keys()),
                                "Molecule 1": list(prop1.values()),
                                "Molecule 2": [
                                    prop2.get(k, "N/A") for k in prop1.keys()
                                ],
                            }
                        )
                        st.success("Comparison completed!")

                        st.divider()
                        ic1, ic2 = st.columns(2)
                        with ic1:
                            st.markdown(f"**Molecule 1** — `{smiles1.strip()}`")
                            try:
                                st.image(generate_2d_image(mol1), use_container_width=True)
                            except Exception:
                                pass
                        with ic2:
                            st.markdown(f"**Molecule 2** — `{smiles2.strip()}`")
                            try:
                                st.image(generate_2d_image(mol2), use_container_width=True)
                            except Exception:
                                pass

                        st.divider()
                        st.dataframe(
                            comparison,
                            use_container_width=True,
                            hide_index=True,
                        )
                    else:
                        st.error("Property comparison is unavailable.")
                except Exception as e:
                    st.error(f"Comparison error: {e}")


elif page == "Report Center":
    st.subheader("📄 Report Center")
    st.write("View and export your molecular analysis history.")

    if st.session_state.molecule_data:
        rows = []
        for item in st.session_state.molecule_data:
            row = {"SMILES": item["SMILES"]}
            if isinstance(item["Properties"], dict):
                row.update(item["Properties"])
            rows.append(row)
        report_df = pd.DataFrame(rows)

        st.dataframe(report_df, use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            csv_data = report_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download Analysis History (CSV)",
                csv_data,
                "molecule_history.csv",
                "text/csv",
                use_container_width=True,
            )
        with c2:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.molecule_data = []
                st.rerun()
    else:
        st.info("No analysis history available. Analyse a molecule first.")


elif page == "About the Lab":
    st.subheader("🧪 About Cheminformatics Virtual Laboratory")
    st.write(
        """
        The Cheminformatics Virtual Laboratory is an educational
        application designed to explore molecular structures and
        understand chemical properties using computational tools.
        """
    )

    st.markdown("### Laboratory Features")
    st.markdown(
        """
        - Molecular SMILES input
        - 2D molecular visualisation
        - 3D molecular visualisation
        - Chemical property calculations
        - Batch molecular analysis
        - Molecule comparison
        - CSV report generation
        """
    )

    st.markdown("### Technologies Used")
    st.markdown(
        """
        - Python
        - Streamlit
        - RDKit
        - Pandas
        - Py3Dmol
        """
    )

    st.divider()
    st.caption("Cheminformatics Virtual Laboratory")
    st.caption("Educational Project")


st.markdown(
    '<div class="footer">Cheminformatics Virtual Laboratory &nbsp;•&nbsp; '
    "Powered by Python &amp; Streamlit</div>",
    unsafe_allow_html=True,
)
