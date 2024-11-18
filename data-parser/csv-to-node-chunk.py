import csv
import nltk
import statistics
from tqdm import tqdm
import os
from pathlib import Path
csv.field_size_limit(2147483647)

def create_output_dir():
    output_dir = Path('chunked_output')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def write_chunk_to_file(chunk_data, output_dir, chunk_number):
    output_file = output_dir / f'chunk_{chunk_number}.csv'
    with open(output_file, 'w', newline='') as file:
        fieldnames = ['title', 'text']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(chunk_data)
    return os.path.getsize(output_file)

def parse_csv(input_file, window_size=200, overlap=50):
    output_dir = create_output_dir()
    current_chunk = []
    current_chunk_size = 0
    chunk_number = 1
    MAX_CHUNK_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    
    print("Processing chunks...")
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in tqdm(reader):
            title = row['title']
            text = row['text']
            sentences = nltk.sent_tokenize(text)
            
            current_window = []
            current_length = 0
            
            for sentence in sentences:
                sentence_length = len(sentence)
                
                if current_length + sentence_length <= window_size:
                    current_window.append(sentence)
                    current_length += sentence_length
                else:
                    window_text = ' '.join(current_window)
                    new_row = {'title': title, 'text': window_text}
                    current_chunk.append(new_row)
                    
                    # Estimate chunk size (rough approximation)
                    estimated_row_size = len(str(new_row).encode('utf-8'))
                    current_chunk_size += estimated_row_size
                    
                    # If chunk size exceeds limit, write to file and start new chunk
                    if current_chunk_size >= MAX_CHUNK_SIZE:
                        actual_size = write_chunk_to_file(current_chunk, output_dir, chunk_number)
                        print(f"\nChunk {chunk_number} written: {actual_size / 1024 / 1024:.2f}MB")
                        chunk_number += 1
                        current_chunk = []
                        current_chunk_size = 0
                    
                    # Start new window with overlap
                    overlap_index = max(0, len(current_window) - overlap)
                    current_window = current_window[overlap_index:] + [sentence]
                    current_length = sum(len(s) for s in current_window)
            
            # Add the last window of current text
            if current_window:
                window_text = ' '.join(current_window)
                new_row = {'title': title, 'text': window_text}
                current_chunk.append(new_row)
                current_chunk_size += len(str(new_row).encode('utf-8'))
    
    # Write any remaining data to the final chunk
    if current_chunk:
        actual_size = write_chunk_to_file(current_chunk, output_dir, chunk_number)
        print(f"\nFinal chunk {chunk_number} written: {actual_size / 1024 / 1024:.2f}MB")

def analyze_sentences(input_file):
    sentence_lengths = []
    total_sentences = 0
    
    print("Analyzing sentence lengths...")
    with open(input_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in tqdm(reader):
            text = row['text']
            sentences = nltk.sent_tokenize(text)
            sentence_lengths.extend([len(s) for s in sentences])
            total_sentences += len(sentences)
    
    median_length = statistics.median(sentence_lengths)
    mean_length = statistics.mean(sentence_lengths)
    max_length = max(sentence_lengths)
    
    print(f"\nSentence Statistics:")
    print(f"Total sentences: {total_sentences}")
    print(f"Median length: {median_length:.2f} characters")
    print(f"Mean length: {mean_length:.2f} characters")
    print(f"Max length: {max_length} characters")
    
    return median_length

# Usage
input_file = 'cleaned_pages.csv'

# First analyze sentences
median_length = analyze_sentences(input_file)

# Adjust window size based on median sentence length
suggested_window_size = median_length * 3
suggested_overlap = median_length

print(f"\nSuggested window size: {suggested_window_size}")
print(f"Suggested overlap: {suggested_overlap}")

# Ask user if they want to proceed with suggested values
response = input("\nUse suggested values? (y/n): ")
if response.lower() == 'y':
    parse_csv(input_file, window_size=int(suggested_window_size), overlap=int(suggested_overlap))
else:
    window_size = int(input("Enter window size: "))
    overlap = int(input("Enter overlap size: "))
    parse_csv(input_file, window_size=window_size, overlap=overlap)