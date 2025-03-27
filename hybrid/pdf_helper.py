from PyPDF2 import PdfReader

def get_pdf_data(file_path, num_pages = 1):
    reader = PdfReader(file_path)
    full_doc_text = ""
    pages = reader.pages
    num_pages = len(pages) 
    
    try:
        for page in range(num_pages):
            current_page = reader.pages[page]
            text = current_page.extract_text()
            full_doc_text += text
    except:
        print("Error reading file")
    finally:
        return full_doc_text
    

def get_chunks(fulltext:str,chunk_length =500) -> list:
    text = fulltext

    chunks = []
    while len(text) > chunk_length:
        last_period_index = text[:chunk_length].rfind('.')
        if last_period_index == -1:
            last_period_index = chunk_length
        chunks.append(text[:last_period_index])
        text = text[last_period_index+1:]
    chunks.append(text)

    return chunks