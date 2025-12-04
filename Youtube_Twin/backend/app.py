from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(app)

from utils.transcript_fetcher import TranscriptFetcher
from utils.embeddings_manager import EmbeddingsManager
from utils.chat_handler import ChatHandler

transcript_fetcher = TranscriptFetcher()
embeddings_manager = EmbeddingsManager(api_key=os.getenv('OPENAI_API_KEY'))
chat_handler = ChatHandler(api_key=os.getenv('OPENAI_API_KEY'))

video_store = {}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "YouTube Twin API is running"}), 200

@app.route('/api/process-video', methods=['POST'])
def process_video():
    """Process a YouTube video and create embeddings"""
    try:
        data = request.json
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({"error": "video_url is required"}), 400
        
        logger.info(f"Processing video: {video_url}")
        
        # Extract video ID
        video_id = transcript_fetcher.extract_video_id(video_url)
        if not video_id:
            return jsonify({"error": "Invalid YouTube URL"}), 400
        
        logger.info(f"Extracted video ID: {video_id}")
        
        if video_id in video_store:
            return jsonify({
                "message": "Video already processed",
                "video_id": video_id,
                "video_info": video_store[video_id]['info']
            }), 200
        
        availability = transcript_fetcher.check_transcript_availability(video_id)
        if not availability['available']:
            error_detail = availability.get('error', 'Unknown error')
            logger.error(f"Transcript not available for {video_id}: {error_detail}")
            return jsonify({
                "error": "Transcript not available for this video",
                "details": "This video may not have captions enabled, may be private/restricted, or may have transcript access disabled by the creator.",
                "video_id": video_id
            }), 400
        
        logger.info(f"Available transcript languages for {video_id}: {availability['languages']}")
        
        transcript_data = transcript_fetcher.fetch_transcript(video_id)
        if not transcript_data:
            return jsonify({
                "error": "Could not fetch transcript",
                "details": "The video transcript could not be retrieved. Please ensure the video has captions/subtitles available.",
                "video_id": video_id
            }), 400
        
        chunks_with_embeddings = embeddings_manager.create_embeddings(transcript_data)
        
        video_store[video_id] = {
            'info': transcript_data['info'],
            'chunks': chunks_with_embeddings
        }
        
        logger.info(f"Successfully processed video {video_id} with {len(chunks_with_embeddings)} chunks")
        
        return jsonify({
            "message": "Video processed successfully",
            "video_id": video_id,
            "video_info": transcript_data['info'],
            "chunks_count": len(chunks_with_embeddings)
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with the video content"""
    try:
        data = request.json
        video_id = data.get('video_id')
        message = data.get('message')
        
        if not video_id or not message:
            return jsonify({"error": "video_id and message are required"}), 400
        
        if video_id not in video_store:
            return jsonify({"error": "Video not found. Please process the video first."}), 404
        
        logger.info(f"Chat query for video {video_id}: {message}")
        
        relevant_chunks = embeddings_manager.find_relevant_chunks(
            message,
            video_store[video_id]['chunks'],
            top_k=5
        )
        
        response = chat_handler.generate_response(
            message,
            relevant_chunks,
            video_store[video_id]['info']
        )
        
        return jsonify({
            "response": response['answer'],
            "sources": response['sources']
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/get-transcript', methods=['POST'])
def get_transcript():
    """Get full transcript with timestamps"""
    try:
        data = request.json
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({"error": "video_id is required"}), 400
        
        if video_id not in video_store:
            return jsonify({"error": "Video not found. Please process the video first."}), 404
        
        chunks = video_store[video_id]['chunks']
        transcript = [{
            'text': chunk['text'],
            'start': chunk['start'],
            'duration': chunk['duration']
        } for chunk in chunks]
        
        return jsonify({
            "video_info": video_store[video_id]['info'],
            "transcript": transcript
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting transcript: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search-transcript', methods=['POST'])
def search_transcript():
    """Semantic search within transcript"""
    try:
        data = request.json
        video_id = data.get('video_id')
        query = data.get('query')
        top_k = data.get('top_k', 3)
        
        if not video_id or not query:
            return jsonify({"error": "video_id and query are required"}), 400
        
        if video_id not in video_store:
            return jsonify({"error": "Video not found. Please process the video first."}), 404
        
        relevant_chunks = embeddings_manager.find_relevant_chunks(
            query,
            video_store[video_id]['chunks'],
            top_k=top_k
        )
        
        results = [{
            'text': chunk['text'],
            'start': chunk['start'],
            'duration': chunk['duration'],
            'similarity': chunk.get('similarity', 0)
        } for chunk in relevant_chunks]
        
        return jsonify({
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching transcript: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
