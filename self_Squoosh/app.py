import io
import zipfile
from pathlib import Path

import streamlit as st
from PIL import Image

WIDTHS = [400, 800, 1200]
WEBP_QUALITY = 80


def resize_to_webp(image: Image.Image, target_width: int) -> bytes:
    """Resize image to target width (keeping aspect ratio) and encode as WebP."""
    ratio = target_width / image.width
    target_height = int(image.height * ratio)
    resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format="WEBP", quality=WEBP_QUALITY)
    return buf.getvalue()


def generate_variants(image: Image.Image) -> dict[int, bytes]:
    """Generate WebP variants for all target widths."""
    variants: dict[int, bytes] = {}
    for w in WIDTHS:
        if w <= image.width:
            variants[w] = resize_to_webp(image, w)
        else:
            variants[w] = resize_to_webp(image, image.width)
    return variants


def build_batch_zip(all_variants: dict[str, dict[int, bytes]]) -> bytes:
    """Pack all images into a ZIP with a folder per image."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for stem, variants in all_variants.items():
            for width, data in variants.items():
                zf.writestr(f"{stem}/{stem}-{width}.webp", data)
    return buf.getvalue()


def html_snippet(stem: str) -> str:
    return f"""\
<img
  src="{stem}-800.webp"
  srcset="
    {stem}-400.webp 400w,
    {stem}-800.webp 800w,
    {stem}-1200.webp 1200w
  "
  sizes="(max-width: 600px) 400px,
         (max-width: 1024px) 800px,
         1200px"
  alt="Optimized image"
/>"""


# ── UI ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Squish", page_icon="🫠", layout="wide")

st.title("🫠 Squish")
st.caption("Upload images → get 3 responsive WebP variants per image + HTML snippets")

uploaded_files = st.file_uploader(
    "Drop your images here",
    type=["png", "jpg", "jpeg", "webp"],
    accept_multiple_files=True,
)

if uploaded_files:
    # Build a cache key from filenames + sizes to detect new uploads
    cache_key = tuple((f.name, f.size) for f in uploaded_files)

    # Only reprocess if uploads changed
    if st.session_state.get("cache_key") != cache_key:
        all_variants: dict[str, dict[int, bytes]] = {}
        total_original = 0
        total_compressed = 0

        progress = st.progress(0, text="Processing images...")

        for i, uploaded in enumerate(uploaded_files):
            image = Image.open(uploaded).convert("RGB")
            stem = Path(uploaded.name).stem

            if stem in all_variants:
                stem = f"{stem}_{i}"

            variants = generate_variants(image)
            all_variants[stem] = variants

            total_original += uploaded.size
            total_compressed += sum(len(d) for d in variants.values())

            progress.progress((i + 1) / len(uploaded_files), text=f"Processing {i + 1}/{len(uploaded_files)}...")

        progress.empty()

        # Cache results in session state
        st.session_state["cache_key"] = cache_key
        st.session_state["all_variants"] = all_variants
        st.session_state["total_original"] = total_original
        st.session_state["total_compressed"] = total_compressed
        st.session_state["zip_bytes"] = build_batch_zip(all_variants)

    # Read from cache
    all_variants = st.session_state["all_variants"]
    total_original = st.session_state["total_original"]
    total_compressed = st.session_state["total_compressed"]
    zip_bytes = st.session_state["zip_bytes"]

    st.success(f"Done! Processed **{len(uploaded_files)}** images")

    # ── Stats ──
    col1, col2, col3 = st.columns(3)
    col1.metric("Images", len(uploaded_files))
    col2.metric("Original total", f"{total_original / 1024:.1f} KB")
    col3.metric("Compressed total", f"{total_compressed / 1024:.1f} KB")

    st.divider()

    # ── Download ZIP ──
    st.download_button(
        f"⬇️  Download all ({len(uploaded_files)} images × 3 sizes) as ZIP",
        data=zip_bytes,
        file_name="squish-responsive.zip",
        mime="application/zip",
    )

    st.divider()

    # ── Preview each image ──
    for stem, variants in all_variants.items():
        with st.expander(f"📁 {stem}", expanded=False):
            cols = st.columns(len(WIDTHS))
            for col, width in zip(cols, WIDTHS):
                data = variants[width]
                with col:
                    st.image(data, caption=f"{width}w", use_column_width=True)
                    st.caption(f"{len(data) / 1024:.1f} KB")

            st.code(html_snippet(stem), language="html")
