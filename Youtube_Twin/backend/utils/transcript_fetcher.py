import re
import os
import logging
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs, urlencode
import time

logger = logging.getLogger(__name__)

class TranscriptFetcher:
    def __init__(self):
        self.chunk_duration = int(os.getenv('CHUNK_DURATION', 30))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 5))
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
    
    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def fetch_transcript(self, video_id):
        """Fetch transcript using multiple methods"""
        
        try:
            result = self._fetch_with_requests(video_id)
            if result:
                return result
        except Exception as e:
            logger.warning(f"Requests method failed: {str(e)}")
        
        try:
            result = self._fetch_with_ytdlp(video_id)
            if result:
                return result
        except Exception as e:
            logger.warning(f"yt-dlp method failed: {str(e)}")
        
        logger.error(f"All methods failed for video {video_id}")
        return None
    
    def _fetch_with_requests(self, video_id):
        """Fetch using requests session"""
        try:
            logger.info(f"Fetching transcript for {video_id} using requests")
            
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            
            logger.info("Fetching video page...")
            response = self.session.get(video_url, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch video page: {response.status_code}")
                return None
            
            html = response.text
            logger.info(f"Got video page ({len(html)} bytes)")
            
            caption_url = self._extract_caption_url(html, video_id)
            
            if not caption_url:
                logger.error("Could not find caption URL")
                return None
            
            logger.info(f"Caption URL: {caption_url[:150]}...")
            
            from urllib.parse import urlparse, parse_qs, urlencode
            
            parsed = urlparse(caption_url)
            params = parse_qs(parsed.query)
            
            essential_params = {
                'v': params.get('v', [video_id]),
                'lang': params.get('lang', ['en']),
            }
            
            essential_params['fmt'] = ['json3']
            
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(essential_params, doseq=True)}"
            
            logger.info(f"Trying with clean URL: {clean_url}")
            
            urls_to_try = [
                caption_url, 
                clean_url, 
                f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en&fmt=json3",  
                f"https://www.youtube.com/api/timedtext?v={video_id}&lang=en",  
            ]
            
            caption_data = None
            
            for idx, url in enumerate(urls_to_try):
                try:
                    logger.info(f"Attempt {idx + 1}: Trying URL variation")
                    time.sleep(1)  
                    
                    caption_response = self.session.get(
                        url,
                        headers={
                            'Referer': video_url,
                            'Accept': '*/*',
                            'Accept-Language': 'en-US,en;q=0.9',
                        },
                        timeout=30
                    )
                    
                    if caption_response.status_code == 200:
                        caption_data = caption_response.text
                        
                        if len(caption_data) > 10:
                            logger.info(f"Success! Got caption data ({len(caption_data)} bytes)")
                            break
                        else:
                            logger.warning(f"Attempt {idx + 1}: Got empty response")
                    else:
                        logger.warning(f"Attempt {idx + 1}: HTTP {caption_response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Attempt {idx + 1} error: {str(e)}")
                    continue
            
            if not caption_data or len(caption_data) < 10:
                logger.error("All caption URL variations failed")
                return None
            
           
            if 'json3' in caption_url or caption_data.strip().startswith('{'):
                transcript_list = self._parse_json3_captions(caption_data)
            else:
                transcript_list = self._parse_xml_captions(caption_data)
            
            if not transcript_list:
                logger.error("Failed to parse transcript")
                return None
            
            logger.info(f"Parsed {len(transcript_list)} transcript entries")
            
            chunks = self._create_chunks_with_timestamps(transcript_list)
            
            return {
                'video_id': video_id,
                'info': {
                    'video_id': video_id,
                    'video_url': f'https://www.youtube.com/watch?v={video_id}',
                    'transcript_type': 'requests-session'
                },
                'chunks': chunks
            }
            
        except requests.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transcript: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            raise
    
    def _fetch_with_ytdlp(self, video_id):
        """Fallback: Use yt-dlp with cookies"""
        try:
            import yt_dlp
            
            logger.info(f"Trying yt-dlp for {video_id}")
            
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitleslangs': ['en'],
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f'https://www.youtube.com/watch?v={video_id}', download=False)
                
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                subtitle_data = subtitles.get('en') or automatic_captions.get('en')
                
                if not subtitle_data:
                    logger.error("No subtitles found via yt-dlp")
                    return None
                
                json3_url = None
                for fmt in subtitle_data:
                    if fmt.get('ext') == 'json3':
                        json3_url = fmt.get('url')
                        break
                
                if not json3_url:
                    logger.error("No json3 format found")
                    return None
                
                response = requests.get(json3_url, timeout=30)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch subtitle: {response.status_code}")
                    return None
                
                transcript_list = self._parse_json3_captions(response.text)
                
                if not transcript_list:
                    return None
                
                chunks = self._create_chunks_with_timestamps(transcript_list)
                
                return {
                    'video_id': video_id,
                    'info': {
                        'video_id': video_id,
                        'video_url': f'https://www.youtube.com/watch?v={video_id}',
                        'transcript_type': 'yt-dlp'
                    },
                    'chunks': chunks
                }
                
        except ImportError:
            logger.error("yt-dlp not installed")
            raise
        except Exception as e:
            logger.error(f"yt-dlp error: {str(e)}")
            raise
    
    def _extract_caption_url(self, html, video_id):
        """Extract caption URL from page HTML"""
        try:
            match = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', html)
            if match:
                try:
                    player_response = json.loads(match.group(1))
                    
                    captions = player_response.get('captions', {})
                    player_captions = captions.get('playerCaptionsTracklistRenderer', {})
                    caption_tracks = player_captions.get('captionTracks', [])
                    
                    for track in caption_tracks:
                        lang = track.get('languageCode', '')
                        if 'en' in lang.lower():
                            base_url = track.get('baseUrl')
                            if base_url:
                                logger.info(f"Found caption track: {lang}")
                                return base_url
                    
                    if caption_tracks:
                        base_url = caption_tracks[0].get('baseUrl')
                        if base_url:
                            logger.info("Using first available caption track")
                            return base_url
                    
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON parse error: {e}")
            
            caption_match = re.search(r'"captionTracks":\s*\[([^\]]+)\]', html)
            if caption_match:
                try:
                    tracks_json = '[' + caption_match.group(1) + ']'
                    tracks = json.loads(tracks_json)
                    
                    for track in tracks:
                        if isinstance(track, dict):
                            base_url = track.get('baseUrl')
                            if base_url:
                                logger.info("Found caption via direct search")
                                return base_url
                except:
                    pass
            
            url_match = re.search(r'"captionTracks".*?"baseUrl":"(https://[^"]+)"', html)
            if url_match:
                url = url_match.group(1)
                url = url.replace('\\u0026', '&').replace('\\/', '/')
                logger.info("Found caption via pattern match")
                return url
            
            logger.warning("Could not extract caption URL from page")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting caption URL: {str(e)}")
            return None
    
    def _parse_json3_captions(self, data):
        """Parse JSON3 format captions"""
        try:
            if not data.strip().startswith('{'):
                return self._parse_xml_captions(data)
            
            caption_json = json.loads(data)
            transcript_list = []
            
            events = caption_json.get('events', [])
            
            for event in events:
                segs = event.get('segs')
                if not segs:
                    continue
                
                start_time = event.get('tStartMs', 0) / 1000.0
                duration = event.get('dDurationMs', 0) / 1000.0
                text = ''.join([seg.get('utf8', '') for seg in segs]).strip()
                
                if text:
                    transcript_list.append({
                        'text': text,
                        'start': start_time,
                        'duration': duration
                    })
            
            return transcript_list
            
        except json.JSONDecodeError:
            return self._parse_xml_captions(data)
        except Exception as e:
            logger.error(f"JSON3 parse error: {str(e)}")
            return []
    
    def _parse_xml_captions(self, data):
        """Parse XML format captions"""
        try:
            if not data.strip().startswith('<'):
                logger.error("Data doesn't look like XML")
                return []
            
            root = ET.fromstring(data)
            transcript_list = []
            
            for text_elem in root.findall('.//text'):
                start = float(text_elem.get('start', 0))
                duration = float(text_elem.get('dur', 0))
                text = text_elem.text or ''
                
                text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                text = text.replace('&#39;', "'").replace('&quot;', '"')
                text = re.sub(r'<[^>]+>', '', text)
                text = text.strip()
                
                if text:
                    transcript_list.append({
                        'text': text,
                        'start': start,
                        'duration': duration
                    })
            
            return transcript_list
            
        except ET.ParseError as e:
            logger.error(f"XML parse error: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing XML: {str(e)}")
            return []
    
    def _create_chunks_with_timestamps(self, transcript_list):
        """Create chunks with timestamps"""
        chunks = []
        current_chunk = {'text': '', 'start': 0, 'end': 0, 'duration': 0}
        
        for i, entry in enumerate(transcript_list):
            text = entry['text']
            start = entry['start']
            duration = entry['duration']
            
            if not current_chunk['text']:
                current_chunk['start'] = start
                current_chunk['text'] = text
                current_chunk['end'] = start + duration
            else:
                chunk_duration = current_chunk['end'] - current_chunk['start']
                
                if chunk_duration >= self.chunk_duration:
                    current_chunk['duration'] = current_chunk['end'] - current_chunk['start']
                    chunks.append(current_chunk.copy())
                    
                    overlap_start = current_chunk['end'] - self.chunk_overlap
                    overlap_text = self._get_overlap_text(transcript_list, i, overlap_start)
                    
                    current_chunk = {
                        'text': overlap_text + ' ' + text if overlap_text else text,
                        'start': overlap_start if overlap_text else start,
                        'end': start + duration
                    }
                else:
                    current_chunk['text'] += ' ' + text
                    current_chunk['end'] = start + duration
        
        if current_chunk['text']:
            current_chunk['duration'] = current_chunk['end'] - current_chunk['start']
            chunks.append(current_chunk)
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _get_overlap_text(self, transcript_list, current_index, overlap_start):
        """Get overlap text"""
        overlap_text = ''
        for j in range(max(0, current_index - 5), current_index):
            if transcript_list[j]['start'] >= overlap_start:
                overlap_text += transcript_list[j]['text'] + ' '
        return overlap_text.strip()
    
    def format_timestamp(self, seconds):
        """Format timestamp"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def check_transcript_availability(self, video_id):
        """Check transcript availability"""
        try:
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            response = self.session.get(video_url, timeout=15)
            
            if response.status_code == 200:
                html = response.text
                has_captions = '"captions"' in html or 'captionTracks' in html
                
                return {
                    'available': has_captions,
                    'languages': ['en'] if has_captions else []
                }
            
            return {'available': False, 'error': f'HTTP {response.status_code}'}
            
        except Exception as e:
            return {'available': False, 'error': str(e)}