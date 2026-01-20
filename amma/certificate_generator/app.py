"""
Certificate Bulk Generator
A Streamlit application for generating bulk certificates from Word templates
with automatic serial number incrementing.
"""

import streamlit as st
import re
import io
import zipfile
from docx import Document
from docx.shared import Pt
from typing import List, Dict, Tuple, Optional


def extract_text_with_positions(doc: Document) -> List[Dict]:
    """Extract all text from document with paragraph and run positions."""
    text_items = []

    for para_idx, paragraph in enumerate(doc.paragraphs):
        full_para_text = paragraph.text
        if full_para_text.strip():
            text_items.append({
                'type': 'paragraph',
                'para_idx': para_idx,
                'text': full_para_text,
                'location': f"Paragraph {para_idx + 1}"
            })

    # Also check tables
    for table_idx, table in enumerate(doc.tables):
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                cell_text = cell.text.strip()
                if cell_text:
                    text_items.append({
                        'type': 'table_cell',
                        'table_idx': table_idx,
                        'row_idx': row_idx,
                        'cell_idx': cell_idx,
                        'text': cell_text,
                        'location': f"Table {table_idx + 1}, Row {row_idx + 1}, Cell {cell_idx + 1}"
                    })

    return text_items


def find_serial_patterns(text: str) -> List[Dict]:
    """Find potential serial number patterns in text."""
    patterns = []

    # Pattern 1: Numbers at end after slash (e.g., /014501)
    matches = re.finditer(r'/(\d{3,})\b', text)
    for match in matches:
        patterns.append({
            'full_match': match.group(0),
            'number': match.group(1),
            'start': match.start(),
            'end': match.end(),
            'pattern_type': 'slash_number'
        })

    # Pattern 2: Standalone numbers (e.g., 014501)
    matches = re.finditer(r'\b(\d{4,})\b', text)
    for match in matches:
        # Avoid duplicates from slash pattern
        already_found = any(p['number'] == match.group(1) for p in patterns)
        if not already_found:
            patterns.append({
                'full_match': match.group(0),
                'number': match.group(1),
                'start': match.start(),
                'end': match.end(),
                'pattern_type': 'standalone_number'
            })

    return patterns


def detect_serial_fields(doc: Document) -> List[Dict]:
    """Automatically detect potential serial number fields in the document."""
    detected_fields = []
    text_items = extract_text_with_positions(doc)

    keywords = ['certificate', 'serial', 'number', 'identification', 'id', 'no.', 'no:', 'ref']

    for item in text_items:
        text_lower = item['text'].lower()

        # Check if line contains serial-related keywords
        has_keyword = any(kw in text_lower for kw in keywords)

        # Find number patterns
        patterns = find_serial_patterns(item['text'])

        if patterns and has_keyword:
            for pattern in patterns:
                detected_fields.append({
                    **item,
                    'pattern': pattern,
                    'suggested': True
                })
        elif patterns:
            for pattern in patterns:
                detected_fields.append({
                    **item,
                    'pattern': pattern,
                    'suggested': False
                })

    return detected_fields


def increment_serial(serial: str, increment: int, preserve_length: bool = True) -> str:
    """Increment a serial number string while preserving format."""
    # Extract numeric part
    num = int(serial)
    new_num = num + increment

    if preserve_length:
        return str(new_num).zfill(len(serial))
    return str(new_num)


def replace_last_occurrence(text: str, old: str, new: str) -> str:
    """Replace only the last occurrence of 'old' with 'new' in 'text'."""
    # Find the last occurrence
    last_pos = text.rfind(old)
    if last_pos == -1:
        return text
    return text[:last_pos] + new + text[last_pos + len(old):]


def replace_in_paragraph(paragraph, old_text: str, new_text: str):
    """Replace text in paragraph while preserving formatting.

    This function carefully handles text replacement to maintain
    the original font size, style, and other formatting.
    """
    full_text = paragraph.text
    if old_text not in full_text:
        return

    runs = paragraph.runs
    if not runs:
        return

    # Simple case: text is entirely within a single run
    for run in runs:
        if old_text in run.text:
            run.text = run.text.replace(old_text, new_text)
            return

    # Complex case: text spans multiple runs
    # Find where the old_text starts and ends across runs
    start_pos = full_text.find(old_text)
    end_pos = start_pos + len(old_text)

    # Build a map of run boundaries
    run_boundaries = []  # [(start, end, run), ...]
    current_pos = 0
    for run in runs:
        run_start = current_pos
        run_end = current_pos + len(run.text)
        run_boundaries.append((run_start, run_end, run))
        current_pos = run_end

    # Find which runs are affected
    for i, (run_start, run_end, run) in enumerate(run_boundaries):
        # Check if this run contains the start of old_text
        if run_start <= start_pos < run_end:
            # This run contains the start of the text to replace
            text_before = run.text[:start_pos - run_start]

            # Check if the entire old_text is within this run
            if end_pos <= run_end:
                # Simple case within one run
                text_after = run.text[end_pos - run_start:]
                run.text = text_before + new_text + text_after
                return
            else:
                # Text spans multiple runs
                # Put the replacement in this run with text before it
                run.text = text_before + new_text

                # Clear text from subsequent runs that are part of old_text
                remaining_to_clear = end_pos - run_end
                for j in range(i + 1, len(run_boundaries)):
                    _, _, next_run = run_boundaries[j]
                    next_run_len = len(next_run.text)

                    if remaining_to_clear >= next_run_len:
                        # Clear entire run
                        next_run.text = ""
                        remaining_to_clear -= next_run_len
                    else:
                        # Partial clear - keep the rest
                        next_run.text = next_run.text[remaining_to_clear:]
                        remaining_to_clear = 0
                        break
                return


def replace_in_table_cell(cell, old_text: str, new_text: str):
    """Replace text in a table cell while preserving formatting."""
    for paragraph in cell.paragraphs:
        replace_in_paragraph(paragraph, old_text, new_text)


def remove_highlighting(doc: Document):
    """Remove all yellow/any highlighting from the document."""
    from docx.oxml.ns import qn

    # Remove highlighting from paragraphs
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.highlight_color = None
            # Also remove via XML if needed
            rPr = run._r.get_or_add_rPr()
            highlight = rPr.find(qn('w:highlight'))
            if highlight is not None:
                rPr.remove(highlight)

    # Remove highlighting from tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.highlight_color = None
                        rPr = run._r.get_or_add_rPr()
                        highlight = rPr.find(qn('w:highlight'))
                        if highlight is not None:
                            rPr.remove(highlight)


def generate_certificate(template_bytes: bytes, field_mappings: List[Dict], increment: int) -> Document:
    """Generate a single certificate with incremented serial numbers."""
    # Create a new document from template bytes
    new_doc = Document(io.BytesIO(template_bytes))

    # Remove all highlighting from the document
    remove_highlighting(new_doc)

    for mapping in field_mappings:
        old_serial = mapping['pattern']['number']
        new_serial = increment_serial(old_serial, increment)
        old_text = mapping['pattern']['full_match']
        # Use replace_last_occurrence to handle cases like "1687/2526/1"
        # where we want to replace only the last "1", not the "1" in "1687"
        new_text = replace_last_occurrence(old_text, old_serial, new_serial)

        if mapping['type'] == 'paragraph':
            para_idx = mapping['para_idx']
            if para_idx < len(new_doc.paragraphs):
                replace_in_paragraph(new_doc.paragraphs[para_idx], old_text, new_text)

        elif mapping['type'] == 'table_cell':
            table_idx = mapping['table_idx']
            row_idx = mapping['row_idx']
            cell_idx = mapping['cell_idx']

            if table_idx < len(new_doc.tables):
                table = new_doc.tables[table_idx]
                if row_idx < len(table.rows):
                    row = table.rows[row_idx]
                    if cell_idx < len(row.cells):
                        replace_in_table_cell(row.cells[cell_idx], old_text, new_text)

        elif mapping['type'] == 'manual':
            # For manual fields, search entire document
            # Search in paragraphs
            for paragraph in new_doc.paragraphs:
                if old_text in paragraph.text:
                    replace_in_paragraph(paragraph, old_text, new_text)

            # Search in tables
            for table in new_doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if old_text in cell.text:
                            replace_in_table_cell(cell, old_text, new_text)

    return new_doc


def save_doc_to_bytes(doc: Document) -> bytes:
    """Save a document to bytes."""
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def create_combined_document(template_bytes: bytes, field_mappings: List[Dict], count: int) -> bytes:
    """Create a single document with all certificates separated by page breaks.

    This function properly preserves the template formatting by copying XML elements
    from each generated certificate into a combined document.
    """
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from copy import deepcopy

    # Generate the first certificate as the base document
    combined_doc = generate_certificate(template_bytes, field_mappings, 0)

    # For remaining certificates, append with page breaks
    for i in range(1, count):
        # Generate each certificate from template
        cert_doc = generate_certificate(template_bytes, field_mappings, i)

        # Get all body elements from cert_doc (excluding sectPr)
        elements_to_copy = []
        for element in cert_doc.element.body:
            if not element.tag.endswith('sectPr'):
                elements_to_copy.append(deepcopy(element))

        if elements_to_copy:
            # Add page break to the first element of this certificate
            first_element = elements_to_copy[0]

            # Check if it's a paragraph (w:p) - add page break before
            if first_element.tag.endswith('}p'):
                # Find or create pPr (paragraph properties)
                pPr = first_element.find(qn('w:pPr'))
                if pPr is None:
                    pPr = OxmlElement('w:pPr')
                    first_element.insert(0, pPr)

                # Add page break before this paragraph
                pageBreakBefore = OxmlElement('w:pageBreakBefore')
                pageBreakBefore.set(qn('w:val'), 'true')
                pPr.append(pageBreakBefore)

            elif first_element.tag.endswith('}tbl'):
                # For tables, insert a page break paragraph before the table
                page_break_para = OxmlElement('w:p')
                pPr = OxmlElement('w:pPr')
                pageBreakBefore = OxmlElement('w:pageBreakBefore')
                pageBreakBefore.set(qn('w:val'), 'true')
                pPr.append(pageBreakBefore)
                page_break_para.append(pPr)
                combined_doc.element.body.append(page_break_para)

            # Append all elements
            for element in elements_to_copy:
                combined_doc.element.body.append(element)

    return save_doc_to_bytes(combined_doc)


def main():
    st.set_page_config(
        page_title="Certificate Bulk Generator",
        page_icon="📜",
        layout="wide"
    )

    st.title("📜 Certificate Bulk Generator")
    st.markdown("Generate multiple certificates from a Word template with automatic serial number incrementing.")

    # Initialize session state
    if 'template_doc' not in st.session_state:
        st.session_state.template_doc = None
    if 'template_bytes' not in st.session_state:
        st.session_state.template_bytes = None
    if 'detected_fields' not in st.session_state:
        st.session_state.detected_fields = []
    if 'selected_fields' not in st.session_state:
        st.session_state.selected_fields = []

    # Sidebar for instructions
    with st.sidebar:
        st.header("Instructions")
        st.markdown("""
        1. **Upload Template**: Upload your Word document template
        2. **Map Fields**: Select which fields contain serial numbers to increment
        3. **Configure**: Set the number of certificates to generate
        4. **Generate**: Download individual files or a combined document
        """)

        st.header("Supported Patterns")
        st.markdown("""
        - `C/KPCC/SE--/2526/014501`
        - `1687/2526/1`
        - Any numeric sequences
        """)

    # Step 1: Upload Template
    st.header("Step 1: Upload Template")

    uploaded_file = st.file_uploader(
        "Upload your Word document template (.docx)",
        type=['docx'],
        help="Upload a Word document that will serve as your certificate template"
    )

    if uploaded_file is not None:
        # Load document
        try:
            st.session_state.template_bytes = uploaded_file.getvalue()
            st.session_state.template_doc = Document(io.BytesIO(st.session_state.template_bytes))
            st.success(f"✅ Template loaded: {uploaded_file.name}")

            # Detect serial fields
            st.session_state.detected_fields = detect_serial_fields(st.session_state.template_doc)

        except Exception as e:
            st.error(f"Error loading document: {str(e)}")
            st.session_state.template_doc = None

    if st.session_state.template_doc is not None:
        # Step 2: Field Mapping
        st.header("Step 2: Map Serial Number Fields")

        if not st.session_state.detected_fields:
            st.warning("No potential serial number fields detected. Please check your document.")
        else:
            st.markdown("Select the fields that should be incremented for each certificate:")

            # Group fields by suggested and other
            suggested = [f for f in st.session_state.detected_fields if f.get('suggested', False)]
            others = [f for f in st.session_state.detected_fields if not f.get('suggested', False)]

            selected_indices = []

            if suggested:
                st.subheader("🎯 Suggested Fields (contain serial-related keywords)")
                for idx, field in enumerate(suggested):
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        if st.checkbox("Select", key=f"suggested_{idx}", value=True):
                            selected_indices.append(st.session_state.detected_fields.index(field))
                    with col2:
                        st.text(field['text'][:100] + "..." if len(field['text']) > 100 else field['text'])
                    with col3:
                        st.caption(f"Serial: **{field['pattern']['number']}** | {field['location']}")

            if others:
                st.subheader("📋 Other Detected Number Fields")
                for idx, field in enumerate(others):
                    col1, col2, col3 = st.columns([1, 3, 2])
                    with col1:
                        if st.checkbox("Select", key=f"other_{idx}", value=False):
                            selected_indices.append(st.session_state.detected_fields.index(field))
                    with col2:
                        st.text(field['text'][:100] + "..." if len(field['text']) > 100 else field['text'])
                    with col3:
                        st.caption(f"Number: **{field['pattern']['number']}** | {field['location']}")

            st.session_state.selected_fields = [st.session_state.detected_fields[i] for i in selected_indices]

            # Manual field entry section
            st.subheader("➕ Add Custom Field Manually")
            st.markdown("If a serial number wasn't detected, you can add it manually by entering the exact text to find and replace.")

            with st.expander("Add manual field", expanded=False):
                manual_search_text = st.text_input(
                    "Text to search for (e.g., '/014501' or '1687/2526/1')",
                    key="manual_search",
                    help="Enter the exact text pattern including the number that should increment"
                )
                manual_number = st.text_input(
                    "Number to increment (e.g., '014501' or '1')",
                    key="manual_number",
                    help="Enter just the numeric part that should increment"
                )

                if st.button("Add Manual Field", key="add_manual"):
                    if manual_search_text and manual_number:
                        # Validate that the number is in the search text
                        if manual_number in manual_search_text:
                            manual_field = {
                                'type': 'manual',
                                'text': f"Manual: {manual_search_text}",
                                'location': "User-defined",
                                'pattern': {
                                    'full_match': manual_search_text,
                                    'number': manual_number,
                                    'pattern_type': 'manual'
                                },
                                'suggested': False
                            }
                            if 'manual_fields' not in st.session_state:
                                st.session_state.manual_fields = []
                            st.session_state.manual_fields.append(manual_field)
                            st.success(f"Added manual field: {manual_search_text}")
                            st.rerun()
                        else:
                            st.error("The number must be contained within the search text.")
                    else:
                        st.error("Please fill in both fields.")

            # Display and select manual fields
            if 'manual_fields' in st.session_state and st.session_state.manual_fields:
                st.subheader("✏️ Manual Fields")
                for idx, field in enumerate(st.session_state.manual_fields):
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 1])
                    with col1:
                        if st.checkbox("Select", key=f"manual_{idx}", value=True):
                            st.session_state.selected_fields.append(field)
                    with col2:
                        st.text(field['pattern']['full_match'])
                    with col3:
                        st.caption(f"Number: **{field['pattern']['number']}**")
                    with col4:
                        if st.button("🗑️", key=f"delete_manual_{idx}"):
                            st.session_state.manual_fields.pop(idx)
                            st.rerun()

        # Step 3: Generation Settings
        st.header("Step 3: Configure Generation")

        col1, col2 = st.columns(2)

        with col1:
            num_certificates = st.number_input(
                "Number of certificates to generate",
                min_value=1,
                max_value=20000,
                value=10,
                help="How many certificates do you want to generate?"
            )

        with col2:
            output_format = st.radio(
                "Output format",
                options=["Individual files (ZIP)", "Combined document"],
                help="Choose how you want to receive the generated certificates"
            )

        # Preview
        if st.session_state.selected_fields:
            st.subheader("Preview")
            st.markdown("**Selected fields will increment as follows:**")

            preview_data = []
            for field in st.session_state.selected_fields:
                serial = field['pattern']['number']
                full_match = field['pattern']['full_match']
                preview_data.append({
                    'Pattern': full_match,
                    'Cert #1': replace_last_occurrence(full_match, serial, increment_serial(serial, 0)),
                    'Cert #2': replace_last_occurrence(full_match, serial, increment_serial(serial, 1)),
                    'Cert #3': replace_last_occurrence(full_match, serial, increment_serial(serial, 2)),
                    f'Cert #{num_certificates}': replace_last_occurrence(full_match, serial, increment_serial(serial, num_certificates - 1))
                })

            st.table(preview_data)

        # Step 4: Generate
        st.header("Step 4: Generate Certificates")

        if not st.session_state.selected_fields:
            st.warning("Please select at least one field to increment.")
        else:
            if st.button("🚀 Generate Certificates", type="primary", use_container_width=True):
                with st.spinner(f"Generating {num_certificates} certificates..."):
                    try:
                        progress_bar = st.progress(0)

                        if output_format == "Individual files (ZIP)":
                            # Create ZIP file with individual documents
                            zip_buffer = io.BytesIO()

                            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                                for i in range(num_certificates):
                                    # Generate certificate from template bytes
                                    cert_doc = generate_certificate(
                                        st.session_state.template_bytes,
                                        st.session_state.selected_fields,
                                        i
                                    )

                                    # Get first serial for filename
                                    first_serial = st.session_state.selected_fields[0]['pattern']['number']
                                    cert_serial = increment_serial(first_serial, i)

                                    # Save to bytes
                                    doc_bytes = save_doc_to_bytes(cert_doc)
                                    zip_file.writestr(f"Certificate_{cert_serial}.docx", doc_bytes)

                                    progress_bar.progress((i + 1) / num_certificates)

                            zip_buffer.seek(0)

                            st.success(f"✅ Generated {num_certificates} certificates!")

                            st.download_button(
                                label="📥 Download ZIP File",
                                data=zip_buffer.getvalue(),
                                file_name="certificates.zip",
                                mime="application/zip",
                                use_container_width=True
                            )

                        else:
                            # Create combined document
                            combined_bytes = create_combined_document(
                                st.session_state.template_bytes,
                                st.session_state.selected_fields,
                                num_certificates
                            )

                            progress_bar.progress(1.0)

                            st.success(f"✅ Generated combined document with {num_certificates} certificates!")

                            st.download_button(
                                label="📥 Download Combined Document",
                                data=combined_bytes,
                                file_name="certificates_combined.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )

                    except Exception as e:
                        st.error(f"Error generating certificates: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Certificate Bulk Generator | Made with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
