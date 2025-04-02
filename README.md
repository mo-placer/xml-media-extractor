# XML Media Extractor

A Streamlit application for extracting and organizing media references from XML files.

## Features

- Extract images, videos, and audio referenced in XML files
- Map page IDs to titles using a book XML
- Generate detailed reports of all media references
- Create CSV files with all media metadata
- **Optional:** Organize media files by type and page association
- Support for uploading zipped files for faster batch processing

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```bash
streamlit run media_extraction_app.py
```

This will launch a web interface where you can:
1. Choose your upload method: individual files or zip archives
2. Upload your XML files (or a zip containing XML files)
3. Optionally upload a book XML file for page title mapping
4. **Choose whether to upload actual media files** (not required for extracting references)
5. Process the files and download the results

#### Important Note
**You don't need to upload the actual media files** to extract references. The app will still generate a complete report with all media filenames, titles, and page associations from just the XML files.

#### Using Zip Files
For large collections of files, you can create zip archives:
- Zip your XML files into a single archive
- Zip your media files into a separate archive (optional)
- Upload these zip files through the app interface

The app will automatically extract files with the correct extensions from the archives.

### Command-line Usage

For batch processing, you can also use the command-line interface:

```bash
python media_extraction.py xml_folder output_folder [--book-xml BOOK_XML] [--media-folder MEDIA_FOLDER]
```

Arguments:
- `xml_folder`: Folder containing XML files
- `output_folder`: Folder to save extraction results
- `--book-xml`: (Optional) Path to the book XML file containing page titles
- `--media-folder`: (Optional) Folder containing the actual media files

## Output

The extraction process generates:
- A detailed report of all media references
- A CSV file with metadata for all found media
- Organized copies of media files (only if media files were provided)

## Deployment on Render

This application is pre-configured for deployment on Render.

1. Fork or clone this repository to your GitHub account
2. Log in to [Render](https://render.com/)
3. From the Render dashboard, click "New" and select "Blueprint"
4. Connect your GitHub account and select this repository
5. Render will automatically detect the configuration in `render.yaml`
6. Click "Apply" to deploy the application

The app will be deployed and accessible via a URL provided by Render. 