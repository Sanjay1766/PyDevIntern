"""Streamlit web interface for the Real-Time Documentation Assistant."""

import streamlit as st
import time
import threading
from pathlib import Path

import config
from git_watcher import GitWatcher
from document_processor import DocumentProcessor
from rag_system import RAGSystem


# Page configuration
st.set_page_config(
    page_title="Real-Time Documentation Assistant",
    page_icon="📚",
    layout="wide"
)


def initialize_system():
    """Initialize the RAG system and Git watcher."""
    if 'initialized' not in st.session_state:
        with st.spinner("Initializing system..."):
            # Initialize RAG system
            st.session_state.rag = RAGSystem()
            st.session_state.processor = DocumentProcessor()
            
            # Initialize Git watcher
            st.session_state.git_watcher = GitWatcher(
                config.DOCS_REPO_URL if config.DOCS_REPO_URL else "",
                config.DOCS_REPO_PATH
            )
            
            # Setup repository
            if st.session_state.git_watcher.setup():
                # Initial indexing
                docs = st.session_state.processor.load_documents_from_directory(
                    config.DOCS_REPO_PATH
                )
                st.session_state.rag.index_documents(docs)
                st.session_state.last_update = time.time()
            else:
                st.error(f"Failed to setup repository at {config.DOCS_REPO_PATH}")
            
            st.session_state.initialized = True
            st.session_state.messages = []


def check_for_updates():
    """Check for Git updates and re-index if needed."""
    if 'git_watcher' in st.session_state:
        try:
            if st.session_state.git_watcher.check_for_updates():
                with st.spinner("Pulling updates..."):
                    if st.session_state.git_watcher.pull_updates():
                        # Re-index changed documents
                        changed_files = st.session_state.git_watcher.get_changed_files()
                        
                        # Remove old versions
                        st.session_state.rag.remove_documents(changed_files)
                        
                        # Index new versions
                        docs = st.session_state.processor.load_documents_from_directory(
                            config.DOCS_REPO_PATH
                        )
                        changed_docs = st.session_state.processor.filter_changed_documents(
                            docs, changed_files
                        )
                        st.session_state.rag.index_documents(changed_docs)
                        
                        st.session_state.last_update = time.time()
                        return True
        except Exception as e:
            st.error(f"Error checking for updates: {e}")
    
    return False


def main():
    """Main application."""
    
    # Initialize system
    initialize_system()
    
    # Sidebar
    with st.sidebar:
        st.title("📚 Real-Time Docs Assistant")
        st.markdown("---")
        
        # System status
        st.subheader("System Status")
        
        if 'rag' in st.session_state:
            stats = st.session_state.rag.get_stats()
            st.metric("Indexed Chunks", stats['total_chunks'])
        
        if 'last_update' in st.session_state:
            time_ago = int(time.time() - st.session_state.last_update)
            st.metric("Last Update", f"{time_ago}s ago")
        
        st.markdown("---")
        
        # Configuration
        st.subheader("Configuration")
        
        if 'git_watcher' in st.session_state and st.session_state.git_watcher.repo:
            st.success("✓ Git repository configured")
            st.text(f"Path: {config.DOCS_REPO_PATH.name}")
            if config.DOCS_REPO_URL:
                st.text(f"URL: {config.DOCS_REPO_URL[:50]}...")
        else:
            st.error("✗ No Git repository configured")
        
        st.success("✓ Ollama LLM configured (local, no API key needed)")
        st.text(f"Model: {config.OLLAMA_MODEL}")
        st.text(f"Base URL: {config.OLLAMA_BASE_URL}")
        
        st.markdown("---")
        
        # Manual update button
        if st.button("🔄 Check for Updates", use_container_width=True):
            if check_for_updates():
                st.success("✓ Updates pulled and indexed!")
            else:
                st.info("No updates available")
        
        st.markdown("---")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # Main content
    st.title("Real-Time Documentation Assistant")
    st.markdown("Ask questions about your documentation. The system automatically stays up-to-date!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📄 Sources"):
                    for source in message["sources"]:
                        st.text(f"• {source}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documentation..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching documentation..."):
                result = st.session_state.rag.query(prompt)
                
                st.markdown(result['answer'])
                
                # Show sources
                if result['sources']:
                    with st.expander("📄 Sources"):
                        for source in result['sources']:
                            st.text(f"• {source}")
                
                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources']
                })
    
    # Auto-check for updates (every 30 seconds)
    if 'last_auto_check' not in st.session_state:
        st.session_state.last_auto_check = time.time()
    
    time_since_check = time.time() - st.session_state.last_auto_check
    if time_since_check > 30:
        check_for_updates()
        st.session_state.last_auto_check = time.time()


if __name__ == "__main__":
    main()
