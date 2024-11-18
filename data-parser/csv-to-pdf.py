import pandas as pd
import pdfkit
import os
import logging
from tqdm import tqdm  # Import tqdm for progress bar
from pdfkit import configuration

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to clean HTML and return readable text
def clean_html_to_text(html_content):
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        logging.debug(f"Cleaned text length: {len(text)}")
        return text
    except Exception as e:
        logging.error(f"Error in clean_html_to_text: {str(e)}")
        return html_content

# Function to generate PDF from HTML content
def generate_pdf(html_content, output_file):
    try:
        # Specify the path to wkhtmltopdf executable
        config = configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        
        # Add more options for debugging
        options = {
            'no-outline': None,
            'encoding': 'UTF-8',
            'page-size': 'A4',
            'debug-javascript': None,
            'enable-local-file-access': None,
            'log-level': 'info'
        }
        
        # Log the HTML content length
        logging.debug(f"HTML content length: {len(html_content)}")
        
        # Check if HTML content is empty
        if not html_content.strip():
            logging.error("HTML content is empty!")
            return
            
        pdfkit.from_string(html_content, output_file, options=options, configuration=config)
        
        # Verify the PDF was created and has content
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            logging.info(f"PDF generated successfully: {output_file} ({os.path.getsize(output_file)} bytes)")
        else:
            logging.error(f"PDF generation failed or file is empty: {output_file}")
            
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        raise

# Function to process CSV and generate PDF
def process_csv(input_csv, output_dir):
    try:
        # Read CSV data
        df = pd.read_csv(input_csv)
        print(df.head())
        print(df['text'].iloc[0])  # Changed from 'Text' to 'text'
        logging.info(f"Read CSV file with {len(df)} rows")
        
        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Iterate over rows in CSV and generate PDF for each with progress bar
        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Generating PDFs"):  # Add progress bar
            # Extract the fields from the row - updated column names
            title = row.get('title', '')  # Changed from 'Title' to 'title'
            html_content = row.get('text', '')  # Changed from 'Text' to 'text'
            
            # Clean up HTML content for readability
            readable_text = clean_html_to_text(html_content)
            
            # Build the full HTML content for the PDF
            html_pdf_content = f"""
            <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                        }}
                        h1 {{
                            text-align: center;
                            color: #4CAF50;
                        }}
                        p {{
                            margin-bottom: 20px;
                        }}
                    </style>
                </head>
                <body>
                    <h1>{title}</h1>
                    <p>{readable_text}</p>
                </body>
            </html>
            """
            
            # Define output PDF filename
            output_pdf = os.path.join(output_dir, f"document_{index + 1}.pdf")
            
            # Generate PDF
            generate_pdf(html_pdf_content, output_pdf)
            logging.info(f"PDF generated: {output_pdf}")  # Log the PDF generation

    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        raise

# Main function to run the script
if __name__ == '__main__':
    input_csv = 'buttercms_pages.csv'  # Path to your CSV file
    output_dir = 'output_pdfs'    # Directory to store the PDFs
    
    # Process the CSV and generate PDFs
    process_csv(input_csv, output_dir)
    logging.info("PDF generation complete.")  # Log completion message
