import streamlit as st
from PIL import Image
import google.generativeai as genai
import io
import os

# ----------------------------
# CONFIGURE GEMINI
# ----------------------------
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY", ""))

text_model = genai.GenerativeModel("gemini-2.5-pro")
image_model = genai.GenerativeModel("gemini-3-pro-image-preview")
 
# ----------------------------
# STREAMLIT CONFIG
# ----------------------------
st.set_page_config(page_title="AI Interior Designer", layout="wide")
st.title("AI Interior Design Studio")
 
# ----------------------------
# STATE INIT (IMPORTANT)
# ----------------------------
if "image" not in st.session_state:
    st.session_state.image = None

if "design_text" not in st.session_state:
    st.session_state.design_text = None

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "edit_history" not in st.session_state:
    st.session_state.edit_history = []

if "ai_suggestions" not in st.session_state:
    st.session_state.ai_suggestions = None

# ----------------------------
# HELPER FUNCTION TO PARSE AI SUGGESTIONS
# ----------------------------
def parse_ai_suggestion(suggestions_text, field_name, options_list):
    """Extract suggested value from AI response"""
    if not suggestions_text:
        return 0

    try:
        lines = suggestions_text.split('\n')
        for line in lines:
            if field_name in line:
                # Extract the value after the colon
                value = line.split(':', 1)[1].strip()
                # Find matching option in the list
                for idx, option in enumerate(options_list):
                    if option.lower() == value.lower() or value.lower() in option.lower():
                        return idx
    except:
        pass
    return 0

# ----------------------------
# UI LAYOUT
# ----------------------------
left, right = st.columns(2)
 
with left:
    uploaded_image = st.file_uploader(
        "Upload Room Image",
        type=["jpg", "jpeg", "png"]
    )
 
    style_options = [
        "No Preference",
        "Modern Minimalist",
        "Contemporary",
        "Luxury/Opulent",
        "Scandinavian",
        "Industrial",
        "Mid-Century Modern",
        "Bohemian/Boho",
        "Traditional",
        "Rustic/Farmhouse",
        "Coastal/Beach",
        "Art Deco",
        "Japanese Zen",
        "Mediterranean",
        "Indian Contemporary",
        "Victorian",
        "Eclectic",
        "Transitional",
        "Custom"
    ]
    style = st.selectbox(
        "Interior Style",
        style_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Interior Style", style_options)
    )
    if style == "Custom":
        style = st.text_input("Specify your custom interior style:", placeholder="e.g., Gothic Revival, Art Nouveau, Futuristic...")

    room_type_options = [
        "No Preference",
        "Living Room",
        "Bedroom",
        "Master Bedroom",
        "Kids Bedroom",
        "Home Office",
        "Study Room",
        "Kitchen",
        "Dining Room",
        "Bathroom",
        "Guest Room",
        "Home Theater",
        "Gym/Fitness Room",
        "Library",
        "Balcony/Patio",
        "Pooja Room",
        "Custom"
    ]
    room_type = st.selectbox(
        "Room Type",
        room_type_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Room Type", room_type_options)
    )
    if room_type == "Custom":
        room_type = st.text_input("Specify your custom room type:", placeholder="e.g., Music Studio, Art Gallery, Wine Cellar...")

    color_theme_options = [
        "No Preference",
        "Neutral (White, Beige, Gray)",
        "Warm (Orange, Red, Yellow)",
        "Cool (Blue, Green, Purple)",
        "Earthy (Brown, Terracotta, Olive)",
        "Monochrome (Black & White)",
        "Pastel (Soft Pink, Mint, Lavender)",
        "Bold & Vibrant",
        "Navy & Gold",
        "Emerald & Brass",
        "Blush & Rose Gold",
        "Charcoal & Copper",
        "Custom"
    ]
    color_theme = st.selectbox(
        "Color Theme",
        color_theme_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Color Theme", color_theme_options)
    )
    if color_theme == "Custom":
        color_theme = st.text_input("Specify your custom color theme:", placeholder="e.g., Sage Green & Cream, Burgundy & Gold, Ocean Blues...")

    budget_options = ["No Preference", "Economy", "Mid-Range", "Premium", "Luxury", "Ultra-Luxury", "Custom"]
    budget = st.selectbox(
        "Budget Level",
        budget_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Budget Level", budget_options)
    )
    if budget == "Custom":
        budget = st.text_input("Specify your custom budget level:", placeholder="e.g., Student-Friendly, Moderate Upgrade, No Budget Limit...")

    ceiling_options = [
        "No Preference",
        "Ceiling Fan",
        "Chandelier",
        "Pendant Lights",
        "Recessed Lighting",
        "POP (Plaster of Paris)",
        "False Ceiling",
        "Exposed Beams",
        "Cove Lighting",
        "Track Lighting",
        "Skylight",
        "Statement Light Fixture",
        "Custom"
    ]
    celink = st.selectbox(
        "Ceiling Design",
        ceiling_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Ceiling Design", ceiling_options)
    )
    if celink == "Custom":
        celink = st.text_input("Specify your custom ceiling design:", placeholder="e.g., Mirrored Ceiling, Cloud Mural, Exposed Trusses...")

    # New category: Flooring
    flooring_options = [
        "No Preference",
        "Hardwood",
        "Marble",
        "Tile/Ceramic",
        "Laminate",
        "Vinyl",
        "Carpet",
        "Concrete/Polished",
        "Bamboo",
        "Stone",
        "Area Rugs",
        "Custom"
    ]
    flooring = st.selectbox(
        "Flooring Preference",
        flooring_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Flooring Preference", flooring_options)
    )
    if flooring == "Custom":
        flooring = st.text_input("Specify your custom flooring:", placeholder="e.g., Cork Flooring, Epoxy, Terrazzo, Reclaimed Wood...")

    # New category: Wall Treatment
    wall_treatment_options = [
        "No Preference",
        "Paint (Solid Color)",
        "Accent Wall",
        "Wallpaper",
        "Textured Paint",
        "Wood Paneling",
        "Exposed Brick",
        "Stone Cladding",
        "Gallery Wall (Art)",
        "Wainscoting",
        "Venetian Plaster",
        "Custom"
    ]
    wall_treatment = st.selectbox(
        "Wall Treatment",
        wall_treatment_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Wall Treatment", wall_treatment_options)
    )
    if wall_treatment == "Custom":
        wall_treatment = st.text_input("Specify your custom wall treatment:", placeholder="e.g., Fabric Wall Panels, Metal Cladding, Living Green Wall...")

    # New category: Furniture Style
    furniture_style_options = [
        "No Preference",
        "Modern/Contemporary",
        "Classic/Traditional",
        "Minimalist",
        "Vintage/Antique",
        "Industrial",
        "Scandinavian",
        "Mid-Century",
        "Modular",
        "Custom Built-in",
        "Custom"
    ]
    furniture_style = st.selectbox(
        "Furniture Style",
        furniture_style_options,
        index=parse_ai_suggestion(st.session_state.ai_suggestions, "Furniture Style", furniture_style_options)
    )
    if furniture_style == "Custom":
        furniture_style = st.text_input("Specify your custom furniture style:", placeholder="e.g., Retro 70s, Asian Fusion, Hollywood Regency...")

    # ----------------------------
    # CUSTOM DESCRIPTION BOX
    # ----------------------------
    st.divider()
    st.subheader("✍️ Additional Custom Instructions")
    custom_description = st.text_area(
        "Describe Your Vision (Optional)",
        placeholder="Example: I want a cozy reading nook by the window, prefer natural materials, avoid dark colors, include indoor plants, make it feel spacious and airy...",
        help="Add any specific requirements, preferences, or ideas that aren't covered by the options above. The AI will incorporate these into the design.",
        height=120
    )
 
with right:
    if uploaded_image:
        st.session_state.image = Image.open(uploaded_image).convert("RGB")
        st.image(
            st.session_state.image,
            caption="Original Room",
            use_container_width=True
        )

        # AI Suggestion Button
        st.divider()
        if st.button("🤖 Don't Know What to Do? Let AI Suggest!", use_container_width=True, type="secondary"):
            with st.spinner("🔍 Analyzing your room and suggesting best options..."):

                suggestion_prompt = """
Analyze this room image and suggest the BEST design options.

Provide your response in EXACTLY this format (one option per line):

Interior Style: [choose ONE from: Modern Minimalist, Contemporary, Luxury/Opulent, Scandinavian, Industrial, Mid-Century Modern, Bohemian/Boho, Traditional, Rustic/Farmhouse, Coastal/Beach, Art Deco, Japanese Zen, Mediterranean, Indian Contemporary, Victorian, Eclectic, Transitional]

Room Type: [choose ONE from: Living Room, Bedroom, Master Bedroom, Kids Bedroom, Home Office, Study Room, Kitchen, Dining Room, Bathroom, Guest Room, Home Theater, Gym/Fitness Room, Library, Balcony/Patio, Pooja Room]

Color Theme: [choose ONE from: Neutral (White, Beige, Gray), Warm (Orange, Red, Yellow), Cool (Blue, Green, Purple), Earthy (Brown, Terracotta, Olive), Monochrome (Black & White), Pastel (Soft Pink, Mint, Lavender), Bold & Vibrant, Navy & Gold, Emerald & Brass, Blush & Rose Gold, Charcoal & Copper]

Budget Level: [choose ONE from: Economy, Mid-Range, Premium, Luxury, Ultra-Luxury]

Ceiling Design: [choose ONE from: Ceiling Fan, Chandelier, Pendant Lights, Recessed Lighting, POP (Plaster of Paris), False Ceiling, Exposed Beams, Cove Lighting, Track Lighting, Skylight, Statement Light Fixture]

Flooring Preference: [choose ONE from: Hardwood, Marble, Tile/Ceramic, Laminate, Vinyl, Carpet, Concrete/Polished, Bamboo, Stone, Area Rugs]

Wall Treatment: [choose ONE from: Paint (Solid Color), Accent Wall, Wallpaper, Textured Paint, Wood Paneling, Exposed Brick, Stone Cladding, Gallery Wall (Art), Wainscoting, Venetian Plaster]

Furniture Style: [choose ONE from: Modern/Contemporary, Classic/Traditional, Minimalist, Vintage/Antique, Industrial, Scandinavian, Mid-Century, Modular, Custom Built-in]

Be specific and choose options that will work BEST together for this space.
"""

                try:
                    response = text_model.generate_content(
                        [suggestion_prompt, st.session_state.image]
                    )

                    st.session_state.ai_suggestions = response.text
                    st.success("✅ AI suggestions ready! The form will auto-fill on next interaction.")
                    st.rerun()

                except Exception as e:
                    error_msg = str(e)
                    if "DeadlineExceeded" in error_msg or "504" in error_msg or "timeout" in error_msg.lower():
                        st.error("⏱️ Request timed out. Please try again.")
                    else:
                        st.error(f"Error getting AI suggestions: {error_msg}")

        # Display AI suggestions if available
        if st.session_state.ai_suggestions:
            with st.expander("🤖 AI Suggestions", expanded=True):
                st.write(st.session_state.ai_suggestions)
                if st.button("Clear Suggestions"):
                    st.session_state.ai_suggestions = None
                    st.rerun()

# ----------------------------
# COMBINED: DESIGN PLAN + IMAGE GENERATION
# ----------------------------
if uploaded_image and st.button("🎨 Generate Interior Design", type="primary"):

    # Step 1: Analyze and create design plan
    with st.spinner("Step 1/2: Analyzing room and creating design plan..."):

        analysis_prompt = f"""
You are a professional interior designer.

Analyze the uploaded {room_type} image.

Requirements:
- Style: {style}
- Color theme: {color_theme}
- Budget: {budget}
- Ceiling design: {celink}
- Flooring: {flooring}
- Wall treatment: {wall_treatment}
- Furniture style: {furniture_style}
- Keep layout unchanged

{f"ADDITIONAL CUSTOM REQUIREMENTS: {custom_description}" if custom_description.strip() else ""}

Provide:
1. Detailed design description
2. Furniture & decor recommendations
3. Lighting plan
4. Color & material palette
5. Flooring details
6. Wall treatment suggestions
7. Ceiling design elements
8. FINAL photorealistic image generation prompt
"""

        try:
            response = text_model.generate_content(
                [analysis_prompt, st.session_state.image]
            )

            st.session_state.design_text = response.text
            st.success("✅ Design plan created!")

        except Exception as e:
            error_msg = str(e)
            if "DeadlineExceeded" in error_msg or "504" in error_msg or "timeout" in error_msg.lower():
                st.error("⏱️ Request timed out creating design plan. Please try again.")
            else:
                st.error(f"❌ Error creating design plan: {error_msg}")
            st.stop()

    # Step 2: Generate image
    with st.spinner("Step 2/2: Generating AI interior image..."):
 
        image_prompt = f"""
STRICT IMAGE EDITING TASK.

Use the uploaded image as the BASE IMAGE.

ABSOLUTE RULES:
- KEEP exact room size and proportions
- KEEP same camera angle
- KEEP walls, doors, windows, ceiling position unchanged
- DO NOT change layout or structure

ONLY CHANGE:
- Room type: {room_type}
- Interior style: {style}
- Color theme: {color_theme}
- Budget level: {budget}
- Ceiling design: {celink}
- Flooring: {flooring}
- Wall treatment: {wall_treatment}
- Furniture style: {furniture_style}
- Furniture, lighting, decor, materials, textures

{f"IMPORTANT CUSTOM REQUIREMENTS TO INCORPORATE: {custom_description}" if custom_description.strip() else ""}

Make it ultra-realistic, interior photography, natural lighting, professional quality.
"""
 
        try:
            image_response = image_model.generate_content(
                [st.session_state.image, image_prompt]
            )

            for part in image_response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    generated_image = Image.open(io.BytesIO(image_bytes))

                    # FORCE SAME SIZE AS ORIGINAL
                    generated_image = generated_image.resize(
                        st.session_state.image.size
                    )

                    # Store generated image in session state
                    st.session_state.generated_image = generated_image
                    st.session_state.edit_history.append({
                        "image": generated_image.copy(),
                        "prompt": "Initial generation"
                    })

            st.success("✅ Interior design generated successfully!")

        except Exception as e:
            error_msg = str(e)
            if "DeadlineExceeded" in error_msg or "504" in error_msg or "timeout" in error_msg.lower():
                st.error("⏱️ Request timed out. The image generation took too long.")
                st.warning("""
                **Tips to avoid timeouts:**
                - Try a smaller image
                - Simplify your custom requirements
                - Try again (server might be busy)
                """)
            else:
                st.error(f"❌ Error generating image: {error_msg}")
            st.stop()

    # Display the generated image
    st.subheader("Generated Interior Design")
    st.image(
        st.session_state.generated_image,
        caption="AI Generated Interior",
        use_container_width=True
    )

    # ----------------------------
    # DISPLAY COMPLETE INFORMATION
    # ----------------------------
    st.divider()

    # Display Design Plan and Prompt (both hidden by default)
    with st.expander("📋 View Design Plan", expanded=False):
        st.write(st.session_state.design_text)

    with st.expander("💡 View Image Generation Prompt", expanded=False):
        st.code(image_prompt, language="text")

    # ----------------------------
    # DOWNLOAD BUTTON
    # ----------------------------
    buffer = io.BytesIO()
    st.session_state.generated_image.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="⬇️ Download Interior Image (PNG)",
        data=buffer,
        file_name="ai_interior_design.png",
        mime="image/png"
    )

# ----------------------------
# DISPLAY EXISTING DESIGN (If already generated)
# ----------------------------
if st.session_state.generated_image is not None and not uploaded_image:
    st.subheader("Current Interior Design")
    st.image(
        st.session_state.generated_image,
        caption=f"Version {len(st.session_state.edit_history)}",
        use_container_width=True
    )

    # Display Design Plan and Prompt (both hidden by default)
    if st.session_state.design_text:
        with st.expander("📋 View Design Plan", expanded=False):
            st.write(st.session_state.design_text)

    # Download button
    buffer = io.BytesIO()
    st.session_state.generated_image.save(buffer, format="PNG")
    buffer.seek(0)

    st.download_button(
        label="⬇️ Download Current Design",
        data=buffer,
        file_name=f"interior_design_v{len(st.session_state.edit_history)}.png",
        mime="image/png"
    )

# ----------------------------
# ITERATIVE EDITING SECTION
# ----------------------------
if st.session_state.generated_image is not None:
    st.divider()
    st.subheader("✏️ Refine Your Design")
    st.write("Not satisfied? Describe what you'd like to change:")

    # Reference image upload (optional)
    st.markdown("**📎 Reference Image (Optional)**")
    st.caption("Upload a reference image if you want to add or replace an element with something specific (e.g., a specific table, sofa, or decor item).")

    reference_file = st.file_uploader(
        "Upload Reference Image",
        type=["png", "jpg", "jpeg", "webp"],
        help="Example: Upload an image of the table you want to add, or a style reference you want to copy",
        key="refinement_reference_uploader"
    )

    reference_image = None
    if reference_file is not None:
        reference_image = Image.open(reference_file)
        st.image(reference_image, caption="Reference Image", width=200)
        st.success("✅ Reference image loaded! Mention it in your edit instructions below.")

    st.markdown("---")

    # Text input for edit instructions
    edit_instruction = st.text_area(
        "Edit Instructions",
        placeholder="Example: Replace the center table with the one from the reference image, add more plants, change curtains to white...",
        help="Describe specific changes you want to make. If you uploaded a reference image, mention how to use it."
    )

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("🔄 Apply Changes", type="primary", disabled=not edit_instruction):
            with st.spinner("Applying your changes..."):

                # Build reference image context if provided
                reference_context = ""
                if reference_image is not None:
                    reference_context = """

REFERENCE IMAGE PROVIDED:
The user has uploaded a reference image showing an item/style they want to incorporate.
Use this reference image to guide the modification - incorporate the referenced element/style as requested by the user.
Match the style, color, and appearance of the reference while maintaining room coherence."""

                refinement_prompt = f"""
STRICT IMAGE REFINEMENT TASK.

Use the current generated interior design image as the BASE.

USER REQUESTED CHANGES:
{edit_instruction}
{reference_context}

ABSOLUTE RULES:
- KEEP the overall room layout, size, and structure
- KEEP the established interior style unless specifically asked to change
- ONLY modify what the user specifically requested
- Maintain consistency with unchanged elements
- If a reference image is provided, incorporate its elements as specified by the user

Apply the requested changes while keeping everything else consistent.
Make it ultra-realistic, interior photography, natural lighting, professional quality.
"""

                try:
                    # Prepare content for generation
                    generation_content = [st.session_state.generated_image, refinement_prompt]

                    # Add reference image if provided
                    if reference_image is not None:
                        generation_content.append(reference_image)

                    refinement_response = image_model.generate_content(generation_content)

                    for part in refinement_response.candidates[0].content.parts:
                        if part.inline_data:
                            refined_image_bytes = part.inline_data.data
                            refined_image = Image.open(io.BytesIO(refined_image_bytes))

                            # Resize to match original
                            refined_image = refined_image.resize(
                                st.session_state.image.size
                            )

                            # Update session state
                            st.session_state.generated_image = refined_image
                            st.session_state.edit_history.append({
                                "image": refined_image.copy(),
                                "prompt": edit_instruction,
                                "has_reference": reference_image is not None
                            })

                            st.success("✅ Changes applied successfully!")
                            st.rerun()

                except Exception as e:
                    error_msg = str(e)
                    if "DeadlineExceeded" in error_msg or "504" in error_msg or "timeout" in error_msg.lower():
                        st.error("⏱️ Request timed out. Please try again with simpler changes.")
                    else:
                        st.error(f"Error applying changes: {error_msg}")

    with col2:
        if len(st.session_state.edit_history) > 1:
            if st.button("↩️ Undo Last Change"):
                # Remove last edit
                st.session_state.edit_history.pop()
                # Restore previous image
                if st.session_state.edit_history:
                    st.session_state.generated_image = st.session_state.edit_history[-1]["image"].copy()
                    st.success("↩️ Undone!")
                    st.rerun()

    with col3:
        if st.button("🗑️ Reset"):
            st.session_state.generated_image = None
            st.session_state.edit_history = []
            st.rerun()

    # Display current generated image
    st.divider()
    st.subheader("Current Design")
    col_img, col_info = st.columns([2, 1])

    with col_img:
        st.image(
            st.session_state.generated_image,
            caption=f"Version {len(st.session_state.edit_history)}",
            use_container_width=True
        )

    with col_info:
        st.write(f"**Edits Made:** {len(st.session_state.edit_history) - 1}")

        # Show edit history
        if len(st.session_state.edit_history) > 1:
            with st.expander("Edit History", expanded=False):
                for i, edit in enumerate(st.session_state.edit_history):
                    if i == 0:
                        st.write(f"**v{i+1}:** Initial generation")
                    else:
                        st.write(f"**v{i+1}:** {edit['prompt'][:50]}...")

        # Download current version
        download_buffer = io.BytesIO()
        st.session_state.generated_image.save(download_buffer, format="PNG")
        download_buffer.seek(0)

        st.download_button(
            label="⬇️ Download Current Version",
            data=download_buffer,
            file_name=f"interior_design_v{len(st.session_state.edit_history)}.png",
            mime="image/png",
            use_container_width=True
        )

    # ----------------------------
    # VIEW ALL VERSIONS
    # ----------------------------
    if len(st.session_state.edit_history) > 1:
        st.divider()
        st.subheader("🎨 Version History - View All Designs")

        with st.expander("📸 View All Versions", expanded=False):
            st.write(f"Total versions: {len(st.session_state.edit_history)}")

            # Display all versions in a grid
            cols_per_row = 3
            for i in range(0, len(st.session_state.edit_history), cols_per_row):
                cols = st.columns(cols_per_row)

                for j in range(cols_per_row):
                    idx = i + j
                    if idx < len(st.session_state.edit_history):
                        with cols[j]:
                            edit = st.session_state.edit_history[idx]

                            # Display image
                            st.image(
                                edit["image"],
                                caption=f"Version {idx + 1}",
                                use_container_width=True
                            )

                            # Display prompt/description
                            if idx == 0:
                                st.caption("🎯 Initial generation")
                            else:
                                st.caption(f"✏️ {edit['prompt'][:60]}...")

                            # Download button for each version
                            version_buffer = io.BytesIO()
                            edit["image"].save(version_buffer, format="PNG")
                            version_buffer.seek(0)

                            st.download_button(
                                label=f"⬇️ v{idx + 1}",
                                data=version_buffer,
                                file_name=f"interior_design_v{idx + 1}.png",
                                mime="image/png",
                                key=f"download_v{idx}",
                                use_container_width=True
                            )

                            # Button to restore this version
                            if idx != len(st.session_state.edit_history) - 1:
                                if st.button(f"🔄 Restore v{idx + 1}", key=f"restore_v{idx}", use_container_width=True):
                                    st.session_state.generated_image = edit["image"].copy()
                                    st.success(f"✅ Restored to Version {idx + 1}!")
                                    st.rerun()

