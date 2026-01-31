"""Document processing utilities for chunking and embedding."""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Represents a document chunk with metadata."""
    content: str
    source: str
    chunk_id: int
    metadata: Dict[str, Any]


class DocumentProcessor:
    """Processes documents for the RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.supported_extensions = {'.md', '.txt', '.py', '.js', '.json', '.yaml', '.yml'}
    
    def load_documents_from_directory(self, directory: Path) -> List[Document]:
        """
        Load all supported documents from a directory.
        
        Args:
            directory: Path to the directory containing documents
            
        Returns:
            List of Document objects
        """
        documents = []
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return documents
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                try:
                    docs = self.load_document(file_path)
                    documents.extend(docs)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
        
        logger.info(f"Loaded {len(documents)} document chunks from {directory}")
        return documents
    
    def load_document(self, file_path: Path) -> List[Document]:
        """
        Load a single document and split it into chunks.
        
        Args:
            file_path: Path to the document
            
        Returns:
            List of Document chunks
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = self.split_text(content)
            
            documents = []
            for idx, chunk in enumerate(chunks):
                doc = Document(
                    content=chunk,
                    source=str(file_path),
                    chunk_id=idx,
                    metadata={
                        'file_name': file_path.name,
                        'file_type': file_path.suffix,
                        'chunk_index': idx,
                        'total_chunks': len(chunks)
                    }
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            return []
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Find the last newline or space before chunk_size
            if end < len(text):
                # Try to break at paragraph
                last_double_newline = text.rfind('\n\n', start, end)
                if last_double_newline > start:
                    end = last_double_newline
                else:
                    # Try to break at sentence
                    last_period = text.rfind('. ', start, end)
                    if last_period > start:
                        end = last_period + 1
                    else:
                        # Try to break at word
                        last_space = text.rfind(' ', start, end)
                        if last_space > start:
                            end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
    
    def filter_changed_documents(self, 
                                  all_docs: List[Document], 
                                  changed_files: List[str]) -> List[Document]:
        """
        Filter documents to only those from changed files.
        
        Args:
            all_docs: All documents
            changed_files: List of changed file paths
            
        Returns:
            Filtered list of documents
        """
        changed_docs = []
        
        for doc in all_docs:
            for changed_file in changed_files:
                if changed_file in doc.source:
                    changed_docs.append(doc)
                    break
        
        return changed_docs


def main():
    """Test the document processor."""
    processor = DocumentProcessor()
    
    # Test with the current directory
    docs = processor.load_documents_from_directory(Path('.'))
    
    print(f"Loaded {len(docs)} document chunks")
    if docs:
        print(f"\nFirst chunk:")
        print(f"Source: {docs[0].source}")
        print(f"Content preview: {docs[0].content[:200]}...")


if __name__ == "__main__":
    main()
