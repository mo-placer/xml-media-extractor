import os
import xml.etree.ElementTree as ET
import argparse
import shutil
import re
from pathlib import Path
from collections import defaultdict

def is_numeric_page_title(page_title):
    """Check if the page title is numeric or starts with a number."""
    return page_title.strip().isdigit() or re.match(r'^\d+', page_title.strip()) is not None

def get_numeric_value(page_title):
    """Extract the numeric value from a page title if it exists."""
    if page_title.strip().isdigit():
        return int(page_title)
    
    # Extract numbers at the beginning
    match = re.match(r'^(\d+)', page_title.strip())
    if match:
        return int(match.group(1))
    
    return float('inf')  # Non-numeric titles go at the end

def sort_media_references(media_references):
    """
    Sort media references by page_title:
    1. Numeric page titles first (100, 200, etc.)
    2. Text-based page titles at the end
    
    Args:
        media_references (dict): Media references dictionary
        
    Returns:
        dict: Sorted media references dictionary
    """
    # Create a list of (key, value) pairs from the dictionary
    items = list(media_references.items())
    
    # Sort the list based on page title
    sorted_items = sorted(items, key=lambda x: (
        # Sort by whether the title is numeric first (numeric comes first)
        not is_numeric_page_title(x[1][4]),
        # Then sort by the numeric value if applicable
        get_numeric_value(x[1][4]),
        # Finally sort by the full page title string
        x[1][4]
    ))
    
    # Convert back to dictionary while preserving order
    return dict(sorted_items)

def extract_media_from_xml(xml_folder, output_folder, book_xml_path=None, media_folder=None):
    """
    Extract all media files referenced in XML files and organize them in the output folder.
    
    Args:
        xml_folder (str): Path to the folder containing XML files
        output_folder (str): Path to save extracted media references
        media_folder (str, optional): Path to the folder containing actual media files
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Dictionary to store media references
    media_references = {}
    
    # Dictionary to map page IDs to their titles from book XML
    page_id_to_title = {}
    
    # Load book XML if provided
    if book_xml_path and os.path.exists(book_xml_path):
        try:
            book_tree = ET.parse(book_xml_path)
            book_root = book_tree.getroot()
            
            # Extract all page_node elements and their titles
            for page_node in book_root.findall('.//page_node'):
                if 'id' in page_node.attrib and 'title' in page_node.attrib:
                    page_id = page_node.attrib['id']
                    page_title = page_node.attrib['title']
                    page_id_to_title[page_id] = page_title
                    
            print(f"Loaded {len(page_id_to_title)} page mappings from book XML")
        except Exception as e:
            print(f"Error loading book XML: {str(e)}")
    
    # Create a report file
    report_path = os.path.join(output_folder, "media_extraction_report.txt")
    
    with open(report_path, 'w') as report:
        report.write("XML Media Extraction Report\n")
        report.write("==========================\n\n")
        
        # Process all XML files in the folder
        xml_files = [f for f in os.listdir(xml_folder) if f.endswith('.xml')]
        report.write(f"Found {len(xml_files)} XML files to process.\n\n")
        
        for xml_file in xml_files:
            xml_path = os.path.join(xml_folder, xml_file)
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                
                # Track media in current file
                file_media = []
                
                # Get the page_node id in different ways
                page_id = None
                page_title = "Unknown Page"
                
                # Check if root has a page_node child
                page_nodes = root.findall('./page_node')
                if page_nodes:
                    page_node = page_nodes[0]  # Get the first page_node
                    if 'id' in page_node.attrib:
                        page_id = page_node.attrib['id']
                    if 'title' in page_node.attrib:
                        page_title = page_node.attrib['title']
                # Or if the root itself is a page_node
                elif root.tag == 'page_node' and 'id' in root.attrib:
                    page_id = root.attrib['id']
                    if 'title' in root.attrib:
                        page_title = root.attrib['title']
                
                # If a book XML was provided, use its title mapping if available
                if page_id and page_id in page_id_to_title:
                    page_title = page_id_to_title[page_id]
                
                # Find all image_node elements in the entire XML tree
                image_nodes = root.findall('.//image_node')
                for img in image_nodes:
                    if 'src' in img.attrib:
                        src = img.attrib['src']
                        title = img.attrib.get('title', 'No Title')
                        file_media.append(('image', src, title, page_id, page_title))
                
                # Find all video_node elements (assuming similar structure)
                video_nodes = root.findall('.//video_node')
                for vid in video_nodes:
                    if 'src' in vid.attrib:
                        src = vid.attrib['src']
                        title = vid.attrib.get('title', 'No Title')
                        file_media.append(('video', src, title, page_id, page_title))
                
                # Also check for audio_node elements
                audio_nodes = root.findall('.//audio_node')
                for audio in audio_nodes:
                    if 'src' in audio.attrib:
                        src = audio.attrib['src']
                        title = audio.attrib.get('title', 'No Title')
                        file_media.append(('audio', src, title, page_id, page_title))
                
                # Log the findings for this file
                if file_media:
                    report.write(f"File: {xml_file}\n")
                    for media_type, src, title, page_id, page_title in file_media:
                        report.write(f"  - {media_type}: {title} (src: {src})\n")
                        report.write(f"    Page: {page_title} (ID: {page_id})\n")
                        # Add to overall media references dict
                        media_references[src] = (media_type, title, xml_file, page_id, page_title)
                    report.write("\n")
                
            except Exception as e:
                report.write(f"Error processing {xml_file}: {str(e)}\n\n")
        
        # Sort media references by page title
        media_references = sort_media_references(media_references)
        
        # Summary section
        report.write("\nSummary\n=======\n")
        report.write(f"Total media files referenced: {len(media_references)}\n")
        report.write(f"Images: {sum(1 for media_type, _, _, _, _ in media_references.values() if media_type == 'image')}\n")
        report.write(f"Videos: {sum(1 for media_type, _, _, _, _ in media_references.values() if media_type == 'video')}\n")
        report.write(f"Audio: {sum(1 for media_type, _, _, _, _ in media_references.values() if media_type == 'audio')}\n\n")
        
        # Create a CSV of all media references
        csv_path = os.path.join(output_folder, "media_references.csv")
        with open(csv_path, 'w') as csv:
            csv.write("media_type,source,title,xml_file,page_id,page_title\n")
            for src, (media_type, title, xml_file, page_id, page_title) in media_references.items():
                # Escape commas in fields that might contain them
                safe_title = f'"{title}"' if ',' in title else title
                safe_page_title = f'"{page_title}"' if ',' in page_title else page_title
                csv.write(f"{media_type},{src},{safe_title},{xml_file},{page_id},{safe_page_title}\n")
        
        report.write(f"CSV export of all media references created at: {csv_path}\n")
        
        # If media folder is provided, copy the files
        if media_folder and os.path.exists(media_folder):
            media_output_folder = os.path.join(output_folder, "media")
            os.makedirs(media_output_folder, exist_ok=True)
            
            # Create a page-based media organization
            page_based_folder = os.path.join(output_folder, "media_by_page")
            os.makedirs(page_based_folder, exist_ok=True)
            
            copied_count = 0
            missing_count = 0
            
            report.write("\nMedia File Copy Results\n=====================\n")
            
            for src in media_references:
                media_type, title, _, page_id, page_title = media_references[src]
                
                # Handle potential path differences
                # Some systems might store just the filename in src, others might have a path
                src_filename = os.path.basename(src)
                
                # Look for the media file in media_folder
                source_path = os.path.join(media_folder, src_filename)
                
                if os.path.exists(source_path):
                    # Create subdirectory for media type
                    type_folder = os.path.join(media_output_folder, media_type + "s")
                    os.makedirs(type_folder, exist_ok=True)
                    
                    # Copy the file to type-based organization
                    dest_path = os.path.join(type_folder, src_filename)
                    shutil.copy2(source_path, dest_path)
                    
                    # Create page-based organization
                    # Format folder name to be safe for filesystem
                    safe_page_title = page_title.replace('/', '-').replace('\\', '-')
                    page_folder = os.path.join(page_based_folder, f"{safe_page_title}")
                    os.makedirs(page_folder, exist_ok=True)
                    
                    # Copy the file to page-based organization
                    page_dest_path = os.path.join(page_folder, src_filename)
                    shutil.copy2(source_path, page_dest_path)
                    
                    copied_count += 1
                else:
                    report.write(f"Missing media file: {src_filename}\n")
                    missing_count += 1
            
            report.write(f"\nCopied {copied_count} media files to {media_output_folder}\n")
            report.write(f"Missing media files: {missing_count}\n")
    
    print(f"Media extraction complete. Report saved to {report_path}")
    return media_references

def main():
    parser = argparse.ArgumentParser(description='Extract media references from XML files')
    parser.add_argument('xml_folder', help='Folder containing XML files')
    parser.add_argument('output_folder', help='Folder to save extraction results')
    parser.add_argument('--book-xml', help='Path to the book XML file containing page titles')
    parser.add_argument('--media-folder', help='Optional folder containing the actual media files')
    
    args = parser.parse_args()
    
    extract_media_from_xml(args.xml_folder, args.output_folder, args.book_xml, args.media_folder)

if __name__ == "__main__":
    main()