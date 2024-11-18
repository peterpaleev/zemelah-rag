import pandas as pd
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_html_to_text(html_content):
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text(separator=' ').strip()
        return text
    except Exception as e:
        logging.error(f"Error in clean_html_to_text: {str(e)}")
        return html_content

def process_csv(input_csv, output_csv):
    try:
        # Read CSV data
        df = pd.read_csv(input_csv)
        logging.info(f"Read CSV file with {len(df)} rows")
        
        # Create new dataframe for cleaned data
        cleaned_data = []
        
        # Iterate over rows in CSV with progress ba
        
        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Cleaning data"):
            title = row.get('title', '').strip()
            html_content = row.get('text', '')
            
            # Clean up HTML content
            cleaned_text = clean_html_to_text(html_content)
            
            # Add to cleaned data
            cleaned_data.append({
                'title': title,
                'cleaned_text': cleaned_text
            })
        
        # Create new dataframe and save to CSV
        cleaned_df = pd.DataFrame(cleaned_data)
        cleaned_df.to_csv(output_csv, index=False)
        logging.info(f"Cleaned CSV saved to: {output_csv}")

    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        raise

if __name__ == '__main__':
    input_csv = 'buttercms_pages.csv'
    output_csv = 'cleaned_pages.csv'
    
    process_csv(input_csv, output_csv)
    logging.info("CSV cleaning complete.") 