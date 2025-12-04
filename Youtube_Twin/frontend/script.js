document.addEventListener('DOMContentLoaded', function() {
    console.log('YouTube Twin loaded successfully!');

    const API_URL = 'http://localhost:5000';

    let currentVideoId = null;
    let ytPlayer = null;

    const videoUrlInput = document.getElementById('videoUrlInput'); 
    const processBtn = document.getElementById('processBtn');
    const videoInputSection = document.getElementById('videoInputSection');
    const chatSection = document.getElementById('chatSection'); 
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const transcriptContent = document.getElementById('transcriptContent');
    const statusMessage = document.getElementById('statusMessage');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const transcriptSearch = document.getElementById('transcriptSearch');
    const searchBtn = document.getElementById('searchBtn');
    const videoTitle = document.getElementById('videoTitle');
    const videoLink = document.getElementById('videoLink');

    if (!videoUrlInput || !processBtn) {
        console.error('Required DOM elements not found!');
        return;
    }

    console.log('All DOM elements found successfully');

    processBtn.addEventListener('click', processVideo);
    sendBtn.addEventListener('click', sendMessage);
    clearChatBtn.addEventListener('click', clearChat);
    searchBtn.addEventListener('click', searchTranscript);

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('suggestion-btn')) {
            const query = e.target.getAttribute('data-query');
            chatInput.value = query;
            sendMessage();
        }
    });

    async function processVideo() {
        const videoUrl = videoUrlInput.value.trim();
        
        if (!videoUrl) {
            showStatus('Please enter a YouTube URL', 'error');
            return;
        }

        console.log('Processing video:', videoUrl);
        
        processBtn.disabled = true;
        processBtn.querySelector('.btn-text').textContent = 'Processing...';
        processBtn.querySelector('.loader').classList.remove('hidden');
        
        try {
            const response = await fetch(`${API_URL}/api/process-video`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ video_url: videoUrl })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to process video');
            }
            
            console.log('Video processed:', data);
            currentVideoId = data.video_id;
            
            showStatus(`Video processed successfully! ${data.chunks_count} chunks created.`, 'success');
            
            loadVideoPlayer(data.video_id);
            
            videoLink.href = data.video_info.video_url;
            
            await loadTranscript();
            
            videoInputSection.classList.add('hidden');
            chatSection.classList.remove('hidden');
            
        } catch (error) {
            console.error('Error processing video:', error);
            showStatus(error.message, 'error');
        } finally {
            processBtn.disabled = false;
            processBtn.querySelector('.btn-text').textContent = 'Process Video';
            processBtn.querySelector('.loader').classList.add('hidden');
        }
    }

    function loadVideoPlayer(videoId) {
        const playerDiv = document.getElementById('videoPlayer');
        
        if (typeof YT === 'undefined' || typeof YT.Player === 'undefined') {
            console.log('YouTube API not ready, retrying...');
            setTimeout(() => loadVideoPlayer(videoId), 500);
            return;
        }
        
        ytPlayer = new YT.Player(playerDiv, {
            height: '100%',
            width: '100%',
            videoId: videoId,
            playerVars: {
                'playsinline': 1,
                'rel': 0
            },
            events: {
                'onReady': () => console.log('YouTube player ready')
            }
        });
    }

    async function loadTranscript() {
        try {
            const response = await fetch(`${API_URL}/api/get-transcript`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ video_id: currentVideoId })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to load transcript');
            }
            
            displayTranscript(data.transcript);
            
        } catch (error) {
            console.error('Error loading transcript:', error);
            transcriptContent.innerHTML = '<div class="error-state"><p>Failed to load transcript</p></div>';
        }
    }

    function displayTranscript(transcript) {
        transcriptContent.innerHTML = '';
        
        transcript.forEach((item) => {
            const div = document.createElement('div');
            div.className = 'transcript-item';
            div.innerHTML = `
                <span class="timestamp">${formatTimestamp(item.start)}</span>
                <p class="transcript-text">${item.text}</p>
            `;
            div.addEventListener('click', () => seekToTime(item.start));
            transcriptContent.appendChild(div);
        });
    }

    async function searchTranscript() {
        const query = transcriptSearch.value.trim();
        
        if (!query || !currentVideoId) return;
        
        searchBtn.disabled = true;
        searchBtn.textContent = 'Searching...';
        
        try {
            const response = await fetch(`${API_URL}/api/search-transcript`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    query: query,
                    top_k: 5
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Search failed');
            }
            
            highlightSearchResults(data.results);
            
        } catch (error) {
            console.error('Error searching:', error);
            showStatus('Search failed. Please try again.', 'error');
        } finally {
            searchBtn.disabled = false;
            searchBtn.textContent = 'Search';
        }
    }

    function highlightSearchResults(results) {
        const allItems = transcriptContent.querySelectorAll('.transcript-item');
        allItems.forEach(item => item.classList.remove('highlighted'));
        
        results.forEach(result => {
            const timestamp = formatTimestamp(result.start);
            allItems.forEach(item => {
                if (item.querySelector('.timestamp').textContent === timestamp) {
                    item.classList.add('highlighted');
                    item.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            });
        });
    }

    async function sendMessage() {
        const message = chatInput.value.trim();
        
        if (!message || !currentVideoId) return;
        
        addMessage(message, 'user');
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        sendBtn.disabled = true;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-indicator';
        typingDiv.innerHTML = '<div class="message-content"><span></span><span></span><span></span></div>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    message: message
                })
            });
            
            const data = await response.json();
            
            typingDiv.remove();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to get response');
            }
            
            addMessage(data.response, 'bot', data.sources);
            
        } catch (error) {
            console.error('Error sending message:', error);
            typingDiv.remove();
            addMessage('Sorry, I encountered an error. Please try again.', 'bot');
        } finally {
            sendBtn.disabled = false;
        }
    }

    function addMessage(text, sender, sources = null) {
        const welcomeMsg = chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) welcomeMsg.remove();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const processedText = processTimestamps(text);
        
        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = '<div class="sources">';
            sourcesHtml += '<p class="sources-title">📚 Sources:</p>';
            sources.forEach(source => {
                sourcesHtml += `
                    <div class="source-item" onclick="seekToTime(${source.timestamp})">
                        <span class="source-timestamp">${source.formatted_time}</span>
                        <p class="source-text">${source.text}</p>
                    </div>
                `;
            });
            sourcesHtml += '</div>';
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${processedText}
                ${sourcesHtml}
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function processTimestamps(text) {
        const timestampRegex = /\[(\d{1,2}):(\d{2})(?::(\d{2}))?\]/g;
        
        return text.replace(timestampRegex, (match, h, m, s) => {
            let seconds;
            if (s !== undefined) {
                seconds = parseInt(h) * 3600 + parseInt(m) * 60 + parseInt(s);
            } else {
                seconds = parseInt(h) * 60 + parseInt(m);
            }
            return `<a href="#" class="timestamp-link" onclick="seekToTime(${seconds}); return false;">${match}</a>`;
        });
    }

    window.seekToTime = function(seconds) {
        if (ytPlayer && ytPlayer.seekTo) {
            ytPlayer.seekTo(seconds, true);
            ytPlayer.playVideo();
            showStatus(`Jumped to ${formatTimestamp(seconds)}`, 'info');
        }
    };

    function formatTimestamp(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
    }

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type}`;
        statusMessage.classList.remove('hidden');
        
        setTimeout(() => {
            statusMessage.classList.add('hidden');
        }, 5000);
    }

    function clearChat() {
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <h4>👋 Hello! I'm your AI assistant.</h4>
                <p>I've analyzed this video. Ask me anything about its content!</p>
                <div class="suggestions">
                    <p><strong>Try asking:</strong></p>
                    <button class="suggestion-btn" data-query="What is this video about?">What is this video about?</button>
                    <button class="suggestion-btn" data-query="Summarize the main points">Summarize the main points</button>
                    <button class="suggestion-btn" data-query="What are the key takeaways?">What are the key takeaways?</button>
                </div>
            </div>
        `;
    }

    console.log('YouTube Twin ready!');
});