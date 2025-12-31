"""LLM service for answer generation with citations."""
from openai import OpenAI
import config
import re
from typing import List, Dict, Any


class LLMService:
    """Handles LLM interactions for answer generation."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in Railway Variables (Settings → Variables) or in your .env file for local development.")
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.model = config.LLM_MODEL
    
    def generate_answer(
        self,
        query: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate grounded answer with citations.
        
        Args:
            query: User query
            retrieved_chunks: List of retrieved chunks with metadata
            
        Returns:
            Dict with answer text and citation mappings
        """
        if not retrieved_chunks:
            return {
                "answer": "I couldn't find relevant information in the documents to answer your question. Please try rephrasing your query or check if the relevant documents have been ingested.",
                "citations": []
            }
        
        # Build context from retrieved chunks
        context_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            chunk_id = chunk["id"]
            text = chunk["text"]
            metadata = chunk.get("metadata", {})
            doc_title = metadata.get("document_title", "Unknown")
            page = metadata.get("page", "?")
            
            context_parts.append(
                f"[{i}] (ID: {chunk_id}, Source: {doc_title}, Page: {page})\n{text}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Create prompt for grounded answer generation
        prompt = f"""You are a helpful assistant that answers questions based ONLY on the provided document context. 

Rules:
1. Answer the question using ONLY information from the provided context
2. Cite your sources using [1], [2], etc. corresponding to the numbered chunks
3. If the answer is not in the context, explicitly state that the information is not available
4. Do not invent numbers, definitions, or claims not supported by the context
5. Be concise but complete

Context:
{context}

Question: {query}

Answer:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides accurate, cited answers based on document context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            answer_text = response.choices[0].message.content.strip()
            
            # Extract citations from answer
            citations = self._extract_citations(answer_text, retrieved_chunks)
            
            return {
                "answer": answer_text,
                "citations": citations
            }
        
        except Exception as e:
            return {
                "answer": f"Error generating answer: {str(e)}",
                "citations": []
            }
    
    def _extract_citations(
        self,
        answer_text: str,
        retrieved_chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract citation references from answer text.
        
        Args:
            answer_text: Generated answer with citation markers
            retrieved_chunks: Retrieved chunks for mapping
            
        Returns:
            List of citation objects with chunk metadata
        """
        citations = []
        
        # Find all citation markers like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        matches = re.findall(citation_pattern, answer_text)
        
        # Map citation numbers to chunks
        citation_map = {}
        for match in matches:
            citation_num = int(match)
            if 1 <= citation_num <= len(retrieved_chunks):
                chunk = retrieved_chunks[citation_num - 1]
                chunk_id = chunk["id"]
                
                if chunk_id not in citation_map:
                    citation_map[chunk_id] = {
                        "id": chunk_id,
                        "document_title": chunk.get("metadata", {}).get("document_title", "Unknown"),
                        "page": chunk.get("metadata", {}).get("page", "?"),
                        "text": chunk["text"],
                        "similarity_score": chunk.get("similarity_score", 0.0)
                    }
                    citations.append(citation_map[chunk_id])
        
        return citations

