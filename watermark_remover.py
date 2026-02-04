import streamlit as st
import requests
from PIL import Image
import io
import zipfile
import time

BASE_URL = "http://65.20.75.5:8000/pyapi"

st.set_page_config(page_title="Watermark Remover", page_icon="🖼️", layout="wide")

st.title("🖼️ Batch Watermark Remover")
st.write("Upload multiple images to remove watermarks from the bottom right corner.")

# Initialize session state for processed images
if "processed_images" not in st.session_state:
    st.session_state.processed_images = []
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False


def process_single_image(file_data, file_name, file_type):
    """Process a single image and return the result"""
    try:
        # Step 1: Upload the image
        files = {"file": (file_name, file_data, file_type)}
        upload_response = requests.post(f"{BASE_URL}/upload", files=files)
        upload_response.raise_for_status()
        upload_data = upload_response.json()

        session_id = upload_data.get("session_id")
        image_id = upload_data.get("image_id")

        if not session_id or not image_id:
            return None, f"Failed to upload: missing session_id or image_id"

        # Step 2: Modify the image to remove watermark
        modify_payload = {
            "session_id": session_id,
            "generated_image_id": image_id,
            "edit_instruction": "Remove the watermark from the bottom right corner of the image. Keep everything else exactly the same."
        }

        modify_response = requests.post(
            f"{BASE_URL}/modify",
            json=modify_payload,
            timeout=300
        )
        modify_response.raise_for_status()
        modify_data = modify_response.json()

        new_image_id = modify_data.get("new_image_id")

        if not new_image_id:
            return None, f"Failed to modify: missing new_image_id"

        # Step 3: Download the modified image
        download_response = requests.get(f"{BASE_URL}/download/{new_image_id}")
        download_response.raise_for_status()

        return download_response.content, None

    except requests.exceptions.Timeout:
        return None, "Request timed out"
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg += f" - {e.response.text}"
        return None, error_msg
    except Exception as e:
        return None, str(e)


# File uploader for multiple files
uploaded_files = st.file_uploader(
    "Choose images",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Selected {len(uploaded_files)} images")

    # Preview section
    with st.expander("Preview uploaded images", expanded=False):
        cols = st.columns(5)
        for idx, file in enumerate(uploaded_files[:10]):  # Show first 10
            with cols[idx % 5]:
                st.image(file, caption=file.name[:15] + "...", use_column_width=True)
        if len(uploaded_files) > 10:
            st.write(f"... and {len(uploaded_files) - 10} more images")

    # Process button
    col1, col2 = st.columns([1, 4])
    with col1:
        start_processing = st.button("Remove Watermarks", type="primary")
    with col2:
        if st.session_state.processed_images:
            st.write(f"Previously processed: {len(st.session_state.processed_images)} images")

    if start_processing:
        # Reset state
        st.session_state.processed_images = []
        st.session_state.processing_complete = False

        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()

        successful = 0
        failed = 0
        failed_files = []

        for idx, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (idx + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")

            # Process the image
            uploaded_file.seek(0)
            image_data, error = process_single_image(
                uploaded_file.getvalue(),
                uploaded_file.name,
                uploaded_file.type
            )

            if image_data:
                successful += 1
                st.session_state.processed_images.append({
                    "name": uploaded_file.name,
                    "data": image_data
                })
            else:
                failed += 1
                failed_files.append({"name": uploaded_file.name, "error": error})

            # Small delay to avoid overwhelming the API
            time.sleep(0.5)

        # Complete
        st.session_state.processing_complete = True
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")

        # Summary
        st.success(f"Completed: {successful} successful, {failed} failed out of {len(uploaded_files)} images")

        if failed_files:
            with st.expander("View failed images"):
                for f in failed_files:
                    st.error(f"{f['name']}: {f['error']}")

# Display results and download options
if st.session_state.processed_images:
    st.divider()
    st.subheader(f"Processed Images ({len(st.session_state.processed_images)})")

    # Download all as ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for img in st.session_state.processed_images:
            # Add "no_watermark_" prefix to filename
            new_name = f"no_watermark_{img['name']}"
            if not new_name.lower().endswith('.png'):
                new_name = new_name.rsplit('.', 1)[0] + '.png'
            zip_file.writestr(new_name, img['data'])

    zip_buffer.seek(0)

    st.download_button(
        label=f"Download All ({len(st.session_state.processed_images)} images) as ZIP",
        data=zip_buffer.getvalue(),
        file_name="watermark_removed_images.zip",
        mime="application/zip",
        type="primary"
    )

    # Preview processed images
    with st.expander("Preview processed images", expanded=True):
        cols = st.columns(4)
        for idx, img in enumerate(st.session_state.processed_images[:12]):  # Show first 12
            with cols[idx % 4]:
                processed_image = Image.open(io.BytesIO(img['data']))
                st.image(processed_image, caption=img['name'][:20], use_column_width=True)

                # Individual download button
                st.download_button(
                    label="Download",
                    data=img['data'],
                    file_name=f"no_watermark_{img['name']}",
                    mime="image/png",
                    key=f"download_{idx}"
                )

        if len(st.session_state.processed_images) > 12:
            st.write(f"... and {len(st.session_state.processed_images) - 12} more images (download ZIP for all)")

st.divider()
st.caption("Powered by AI Interior Design API")
