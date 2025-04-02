import streamlit as st
import os
import tempfile
import shutil
from media_extraction import extract_media_from_xml
import zipfile
import io

st.set_page_config(
    page_title="XML Media Extractor",
    page_icon="🖼️",
    layout="wide"
)

st.title("XML Media Extractor")
st.markdown("This app extracts and organizes media references from XML files.")

# Create tabs for the application
tab1, tab2 = st.tabs(["Extract Media", "About"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Input Files")
        
        # Option to choose between individual files or zip upload
        upload_mode = st.radio("Upload Method", ["Individual Files", "Zip Files"])
        
        if upload_mode == "Individual Files":
            # File uploaders for individual files
            uploaded_xml_files = st.file_uploader("Upload XML files", type=["xml"], accept_multiple_files=True)
            uploaded_book_xml = st.file_uploader("Upload Book XML (optional)", type=["xml"])
            
            # Checkbox to determine if user wants to upload media files
            include_media = st.checkbox("I want to upload the actual media files", value=False,
                                        help="Uncheck this if you only want to extract media references without uploading the actual media files")
            
            if include_media:
                uploaded_media = st.file_uploader("Upload Media Files", 
                                                 type=["jpg", "jpeg", "png", "gif", "mp4", "mov", "mp3", "wav", "ogg"], 
                                                 accept_multiple_files=True)
            else:
                uploaded_media = None
                st.info("Media files will be referenced in the report but not copied or organized since you're not uploading the actual files.")
        else:
            # File uploaders for zip files
            uploaded_xml_zip = st.file_uploader("Upload XML files as ZIP", type=["zip"])
            uploaded_book_xml = st.file_uploader("Upload Book XML (optional)", type=["xml"])
            
            # Checkbox to determine if user wants to upload media files
            include_media = st.checkbox("I want to upload the actual media files", value=False,
                                        help="Uncheck this if you only want to extract media references without uploading the actual media files")
            
            if include_media:
                uploaded_media_zip = st.file_uploader("Upload Media Files as ZIP", type=["zip"])
            else:
                uploaded_media_zip = None
                st.info("Media files will be referenced in the report but not copied or organized since you're not uploading the actual files.")
    
    with col2:
        st.subheader("Output Options")
        download_options = st.multiselect(
            "Select download options", 
            ["CSV of Media References", "Extraction Report", "All Files (ZIP)"],
            default=["CSV of Media References"]
        )
        
        st.subheader("What you'll get")
        st.markdown("""
        The extraction will generate:
        - A complete report of all media references found in the XML files
        - A CSV file with all media metadata including source filenames, titles, and pages
        - If you uploaded media files: organized copies of those files by type and page
        """)
        
        st.info("You don't need to upload the actual media files to get the reference information.")
    
    # Process button
    process_button_disabled = False
    if upload_mode == "Individual Files" and not uploaded_xml_files:
        process_button_disabled = True
    elif upload_mode == "Zip Files" and not uploaded_xml_zip:
        process_button_disabled = True
        
    if st.button("Extract Media", type="primary", disabled=process_button_disabled):
        with st.spinner("Processing files..."):
            # Create temporary directories
            temp_dir = tempfile.mkdtemp()
            xml_folder = os.path.join(temp_dir, "xml")
            media_folder = os.path.join(temp_dir, "media") if include_media else None
            output_folder = os.path.join(temp_dir, "output")
            
            os.makedirs(xml_folder, exist_ok=True)
            if media_folder:
                os.makedirs(media_folder, exist_ok=True)
            os.makedirs(output_folder, exist_ok=True)
            
            # Handle individual files or zip files based on upload mode
            if upload_mode == "Individual Files":
                # Save uploaded XML files
                for xml_file in uploaded_xml_files:
                    with open(os.path.join(xml_folder, xml_file.name), "wb") as f:
                        f.write(xml_file.getbuffer())
                
                # Save media files if provided and opted in
                if include_media and uploaded_media:
                    for media_file in uploaded_media:
                        with open(os.path.join(media_folder, media_file.name), "wb") as f:
                            f.write(media_file.getbuffer())
            else:
                # Extract XML zip file
                if uploaded_xml_zip:
                    with zipfile.ZipFile(io.BytesIO(uploaded_xml_zip.getvalue())) as zip_ref:
                        # Extract only XML files
                        for file in zip_ref.namelist():
                            if file.lower().endswith('.xml') and not file.startswith('__MACOSX/') and not file.startswith('.'):
                                # Extract the file
                                zip_ref.extract(file, xml_folder)
                    
                    # Move XML files from any subdirectories to the xml_folder
                    for root, _, files in os.walk(xml_folder):
                        if root != xml_folder:
                            for file in files:
                                if file.lower().endswith('.xml'):
                                    src_path = os.path.join(root, file)
                                    dst_path = os.path.join(xml_folder, file)
                                    # Rename if file already exists
                                    counter = 1
                                    base, ext = os.path.splitext(dst_path)
                                    while os.path.exists(dst_path):
                                        dst_path = f"{base}_{counter}{ext}"
                                        counter += 1
                                    shutil.move(src_path, dst_path)
                
                # Extract media zip file if provided and opted in
                if include_media and uploaded_media_zip:
                    with zipfile.ZipFile(io.BytesIO(uploaded_media_zip.getvalue())) as zip_ref:
                        # Extract media files with common extensions
                        media_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.mp3', '.wav', '.ogg')
                        for file in zip_ref.namelist():
                            if file.lower().endswith(media_extensions) and not file.startswith('__MACOSX/') and not file.startswith('.'):
                                # Extract the file
                                zip_ref.extract(file, media_folder)
                    
                    # Move media files from any subdirectories to the media_folder
                    for root, _, files in os.walk(media_folder):
                        if root != media_folder:
                            for file in files:
                                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.mp3', '.wav', '.ogg')):
                                    src_path = os.path.join(root, file)
                                    dst_path = os.path.join(media_folder, file)
                                    # Rename if file already exists
                                    counter = 1
                                    base, ext = os.path.splitext(dst_path)
                                    while os.path.exists(dst_path):
                                        dst_path = f"{base}_{counter}{ext}"
                                        counter += 1
                                    shutil.move(src_path, dst_path)
            
            # Save book XML if provided
            book_xml_path = None
            if uploaded_book_xml:
                book_xml_path = os.path.join(temp_dir, "book.xml")
                with open(book_xml_path, "wb") as f:
                    f.write(uploaded_book_xml.getbuffer())
            
            # Count the number of XML files to process
            xml_files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]
            
            if not xml_files:
                st.error("No XML files found! Please check your uploads.")
            else:
                # Run extraction
                with st.status(f"Processing {len(xml_files)} XML files..."):
                    st.write("Starting media extraction...")
                    media_references = extract_media_from_xml(
                        xml_folder, 
                        output_folder, 
                        book_xml_path, 
                        media_folder
                    )
                    st.write("Extraction complete!")
                
                # Display results
                report_path = os.path.join(output_folder, "media_extraction_report.txt")
                csv_path = os.path.join(output_folder, "media_references.csv")
                
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        report_text = f.read()
                        st.subheader("Extraction Report")
                        st.text_area("Report", report_text, height=400)
                
                # Create a download section
                st.subheader("Download Results")
                
                # Downloads section
                download_col1, download_col2, download_col3 = st.columns(3)
                
                # CSV Download
                if "CSV of Media References" in download_options and os.path.exists(csv_path):
                    with open(csv_path, "r") as f:
                        csv_data = f.read()
                        with download_col1:
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name="media_references.csv",
                                mime="text/csv"
                            )
                
                # Report Download
                if "Extraction Report" in download_options and os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        report_data = f.read()
                        with download_col2:
                            st.download_button(
                                label="Download Report",
                                data=report_data,
                                file_name="media_extraction_report.txt",
                                mime="text/plain"
                            )
                
                # ZIP Download (all files)
                if "All Files (ZIP)" in download_options:
                    with download_col3:
                        # Create a ZIP file with all outputs
                        zip_buffer = io.BytesIO()
                        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                            for root, _, files in os.walk(output_folder):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arc_name = os.path.relpath(file_path, output_folder)
                                    zip_file.write(file_path, arc_name)
                        
                        zip_buffer.seek(0)
                        st.download_button(
                            label="Download ZIP",
                            data=zip_buffer,
                            file_name="media_extraction_results.zip",
                            mime="application/zip"
                        )
                
                # Clean up temp directory (do this after the download buttons are created)
                shutil.rmtree(temp_dir)
                
                media_count = len(media_references) if media_references else 0
                st.success(f"Successfully processed {len(xml_files)} XML files and found {media_count} media references!")

with tab2:
    st.subheader("About XML Media Extractor")
    st.markdown("""
    This application extracts media references from XML files and organizes them.
    
    ### Features:
    - Extract images, videos, and audio referenced in XML files
    - Map page IDs to titles using a book XML
    - Generate detailed reports of all media references
    - Create CSV files with all media metadata
    - Organize media files by type and page association (optional)
    - Support for uploading zipped files for faster batch processing
    
    ### How to use:
    1. Choose your upload method: individual files or zip archives
    2. Upload your XML files (or a zip containing XML files)
    3. (Optional) Upload a book XML file for page title mapping
    4. Decide if you want to upload the actual media files or just extract references
    5. Click 'Extract Media' to process
    6. View the report and download results
    
    ### Important Note:
    You can extract all media references without uploading the actual media files. The app will 
    still generate a complete report with all media filenames, titles, and page associations.
    """)

    st.info("This app is based on the media_extraction.py script.") 