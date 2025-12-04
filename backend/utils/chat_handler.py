from openai import OpenAI
import os
import logging

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.chat_model = os.getenv('CHAT_MODEL', 'gpt-4-turbo-preview')
    
    def generate_response(self, query, relevant_chunks, video_info):
        """Generate a response using GPT with relevant context"""
        try:
            context = self._build_context(relevant_chunks, video_info)
            
            system_message = """You are an AI assistant that helps users understand YouTube video content. 
You have access to the video transcript with timestamps. When answering questions:
1. Provide accurate information based on the transcript
2. Reference specific timestamps when relevant
3. Be conversational and helpful
4. If information isn't in the transcript, say so
5. Format timestamps as clickable references [MM:SS]"""
            
            user_message = f"""Based on the following video transcript excerpts, please answer the question.

Video: {video_info['video_url']}

Transcript Context:
{context}

Question: {query}

Please provide a detailed answer with timestamp references where appropriate."""

            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            sources = self._extract_sources(relevant_chunks)
            
            logger.info(f"Generated response for query: {query}")
            
            return {
                'answer': answer,
                'sources': sources
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise
    
    def _build_context(self, relevant_chunks, video_info):
        """Build context string from relevant chunks"""
        context_parts = []
        
        for i, chunk in enumerate(relevant_chunks, 1):
            timestamp = self._format_timestamp(chunk['start'])
            similarity = chunk.get('similarity', 0)
            
            context_parts.append(
                f"[{timestamp}] (Relevance: {similarity:.2f})\n{chunk['text']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def _extract_sources(self, relevant_chunks):
        """Extract source information with timestamps"""
        sources = []
        
        for chunk in relevant_chunks:
            sources.append({
                'text': chunk['text'][:200] + '...' if len(chunk['text']) > 200 else chunk['text'],
                'timestamp': chunk['start'],
                'formatted_time': self._format_timestamp(chunk['start']),
                'similarity': chunk.get('similarity', 0)
            })
        
        return sources
    
    def _format_timestamp(self, seconds):
        """Format seconds to MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"