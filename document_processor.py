"""Document processing and chunking."""
import fitz  # PyMuPDF
import hashlib
import tiktoken
from typing import List, Dict, Any, Optional
import config
from pathlib import Path


class DocumentProcessor:
    """Processes documents and creates chunks."""
    
    def __init__(self):
        """Initialize tokenizer."""
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Process PDF file and extract text with metadata.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dict with text, pages, and metadata
            
        Raises:
            Exception: If PDF cannot be opened or processed
        """
        # Verify file exists and is readable
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Try to open PDF
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF file '{file_path}': {str(e)}. Please ensure the file is a valid PDF.")
        
        pages = []
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages.append({
                    "page_number": page_num + 1,
                    "text": text
                })
        finally:
            doc.close()
        
        if len(pages) == 0:
            raise ValueError(f"PDF file appears to be empty or has no extractable text: {file_path}")
        
        # Extract title from content or use filename
        title = self.extract_title_from_content({
            "pages": pages,
            "title": Path(file_path).stem
        })
        
        return {
            "title": title or Path(file_path).stem,
            "pages": pages,
            "total_pages": len(pages)
        }
    
    def process_text_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process plain text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dict with text and metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Extract title from content or use filename
        title = self.extract_title_from_content({
            "pages": [{"page_number": 1, "text": text}],
            "title": Path(file_path).stem
        })
        
        return {
            "title": title or Path(file_path).stem,
            "pages": [{"page_number": 1, "text": text}],
            "total_pages": 1
        }
    
    def extract_title_from_content(self, document_data: Dict[str, Any]) -> Optional[str]:
        """
        Extract a meaningful title from document content.
        
        Args:
            document_data: Document data with pages
            
        Returns:
            Extracted title or None
        """
        try:
            # Get first page text
            if not document_data.get("pages"):
                return None
            
            first_page_text = document_data["pages"][0].get("text", "").strip()
            if not first_page_text:
                return None
            
            # Look for title patterns:
            # 1. First line if it's short and looks like a title
            lines = first_page_text.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if not line:
                    continue
                
                # Skip very short or very long lines
                if len(line) < 5 or len(line) > 200:
                    continue
                
                # Skip lines that look like metadata (dates, page numbers, etc.)
                if any(pattern in line.lower() for pattern in ['page', 'date:', 'copyright', '©']):
                    continue
                
                # If line ends with punctuation, it's likely a title
                if line and line[-1] in ['.', '!', '?'] and len(line) < 150:
                    return line.strip()
                
                # If line is reasonably short and on first line, use it
                if len(line) < 100 and lines.index(line) < 2:
                    return line
            
            # Fallback: use first sentence if it's short
            first_sentence = first_page_text.split('.')[0].strip()
            if 10 <= len(first_sentence) <= 100:
                return first_sentence
            
            return None
        except Exception:
            return None
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = None,
        chunk_overlap: int = None
    ) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap size in tokens
            
        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = config.CHUNK_SIZE
        if chunk_overlap is None:
            chunk_overlap = config.CHUNK_OVERLAP
        
        # Tokenize text
        tokens = self.tokenizer.encode(text)
        
        if len(tokens) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - chunk_overlap
        
        return chunks
    
    def create_chunks(
        self,
        document_data: Dict[str, Any],
        document_id: int
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from document data.
        
        Args:
            document_data: Processed document data
            pages: List of page dicts with page_number and text
            document_id: Database document ID
            
        Returns:
            List of chunk dicts ready for embedding
        """
        chunks = []
        chunk_index = 0
        
        for page_data in document_data["pages"]:
            page_number = page_data["page_number"]
            page_text = page_data["text"]
            
            # Chunk the page text
            page_chunks = self.chunk_text(page_text)
            
            for chunk_text in page_chunks:
                chunk = {
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "metadata": {
                        "document_id": str(document_id),
                        "document_title": document_data["title"],
                        "page": page_number,
                        "chunk_index": chunk_index
                    }
                }
                chunks.append(chunk)
                chunk_index += 1
        
        return chunks
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file for idempotency."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

