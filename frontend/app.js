/**
 * StrunzKnowledge Chat Frontend
 * Auth-less client using Gemini API for intelligent health insights
 */

class StrunzKnowledgeChat {
    constructor() {
        this.geminiKey = null;
        this.mcpServerUrl = 'https://strunz.up.railway.app';
        this.isConnected = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.checkMCPServer();
        this.loadSavedKey();
    }

    initializeElements() {
        // Setup elements
        this.setupPanel = document.getElementById('setup-panel');
        this.geminiKeyInput = document.getElementById('gemini-key');
        this.saveKeyBtn = document.getElementById('save-key');
        
        // Chat elements
        this.chatContainer = document.getElementById('chat-container');
        this.chatMessages = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.sendBtn = document.getElementById('send-btn');
        
        // Status elements
        this.statusText = document.getElementById('status-text');
        this.mcpStatus = document.getElementById('mcp-connection');
        
        // Tool selector
        this.toolRadios = document.querySelectorAll('input[name="tool"]');
    }

    attachEventListeners() {
        this.saveKeyBtn.addEventListener('click', () => this.saveApiKey());
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
        
        // Allow saving key with Enter
        this.geminiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.saveApiKey();
        });
    }

    loadSavedKey() {
        const savedKey = localStorage.getItem('gemini_api_key');
        if (savedKey) {
            this.geminiKey = savedKey;
            this.geminiKeyInput.value = savedKey;
            this.connectWithKey();
        }
    }

    async checkMCPServer() {
        try {
            const response = await fetch(`${this.mcpServerUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'ok') {
                this.mcpStatus.textContent = '✅ Connected';
                this.mcpStatus.style.color = '#48bb78';
                
                // Check if Gemini tools are available
                if (data.gemini_integration && data.gemini_integration.available) {
                    this.mcpStatus.textContent += ' (Gemini Enhanced)';
                }
            }
        } catch (error) {
            this.mcpStatus.textContent = '❌ Offline';
            this.mcpStatus.style.color = '#e53e3e';
        }
    }

    saveApiKey() {
        const key = this.geminiKeyInput.value.trim();
        if (!key) {
            alert('Please enter your Gemini API key');
            return;
        }
        
        this.geminiKey = key;
        localStorage.setItem('gemini_api_key', key);
        this.connectWithKey();
    }

    async connectWithKey() {
        try {
            // Test the Gemini API key
            const testResponse = await this.callGeminiAPI('Hello, respond with "OK" if you can hear me.');
            
            if (testResponse.includes('OK') || testResponse.length > 0) {
                this.isConnected = true;
                this.setupPanel.style.display = 'none';
                this.chatContainer.style.display = 'flex';
                this.chatInput.disabled = false;
                this.sendBtn.disabled = false;
                this.statusText.textContent = '🟢 Connected';
                this.statusText.classList.add('connected');
                this.chatInput.focus();
            }
        } catch (error) {
            alert('Invalid API key or connection error. Please check your key.');
            console.error('Connection error:', error);
        }
    }

    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Get selected tool
        const selectedTool = document.querySelector('input[name="tool"]:checked').value;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Show loading message
        const loadingId = this.addLoadingMessage();
        
        try {
            let response;
            
            switch (selectedTool) {
                case 'search':
                    response = await this.searchKnowledge(message);
                    break;
                case 'ask':
                    response = await this.askDrStrunz(message);
                    break;
                case 'analyze':
                    response = await this.analyzeHealthTopic(message);
                    break;
                default:
                    response = await this.searchKnowledge(message);
            }
            
            // Remove loading message
            this.removeMessage(loadingId);
            
            // Add assistant response
            this.addMessage(response, 'assistant', true);
            
        } catch (error) {
            this.removeMessage(loadingId);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            console.error('Chat error:', error);
        }
    }

    async searchKnowledge(query) {
        // First, try to use MCP server's Gemini-enhanced search if available
        try {
            const response = await this.callMCPTool('search_knowledge_gemini', {
                query: query,
                limit: 5
            });
            
            if (response.status === 'success') {
                return this.formatSearchResponse(response);
            }
        } catch (error) {
            console.log('Falling back to direct Gemini search');
        }
        
        // Fallback to direct Gemini API
        const prompt = `
As an expert on Dr. Ulrich Strunz's health and nutrition knowledge, search for information about: "${query}"

Provide relevant findings from Dr. Strunz's work, including:
1. Key insights and recommendations
2. Scientific backing if available
3. Practical applications
4. Specific vitamins, minerals, or supplements mentioned

Format your response in a clear, helpful way.`;

        return await this.callGeminiAPI(prompt);
    }

    async askDrStrunz(question) {
        const prompt = `
You are an AI assistant with deep knowledge of Dr. Ulrich Strunz's health philosophy and recommendations.

Based on Dr. Strunz's teachings, please answer this question: "${question}"

Provide:
1. A direct answer based on Dr. Strunz's principles
2. Specific recommendations (vitamins, minerals, lifestyle changes)
3. The scientific reasoning Dr. Strunz would use
4. Practical action steps

Keep the response helpful and actionable.`;

        return await this.callGeminiAPI(prompt);
    }

    async analyzeHealthTopic(topic) {
        const prompt = `
Provide a comprehensive analysis of "${topic}" from Dr. Strunz's perspective.

Include:
1. Overview of Dr. Strunz's approach to this topic
2. Key nutrients and supplements involved
3. Lifestyle recommendations
4. Common misconceptions to avoid
5. Practical implementation tips

Structure your analysis to be thorough yet accessible.`;

        return await this.callGeminiAPI(prompt);
    }

    async callGeminiAPI(prompt) {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${this.geminiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{
                        text: prompt
                    }]
                }],
                generationConfig: {
                    temperature: 0.7,
                    topP: 0.95,
                    maxOutputTokens: 2048,
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Gemini API error: ${response.status}`);
        }

        const data = await response.json();
        return data.candidates[0].content.parts[0].text;
    }

    async callMCPTool(toolName, params) {
        // This would call the MCP server's SSE endpoint
        // For now, we'll implement a simplified version
        const response = await fetch(`${this.mcpServerUrl}/api/tools/${toolName}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(params)
        });

        if (!response.ok) {
            throw new Error(`MCP server error: ${response.status}`);
        }

        return await response.json();
    }

    formatSearchResponse(response) {
        let formatted = `**Search Results for "${response.query}"**\n\n`;
        
        if (response.answer) {
            formatted += response.answer + '\n\n';
        }
        
        if (response.key_concepts && response.key_concepts.length > 0) {
            formatted += '**Key Concepts:** ' + response.key_concepts.join(', ') + '\n\n';
        }
        
        if (response.sources_used && response.sources_used.length > 0) {
            formatted += '**Sources:** ' + response.sources_used.join(', ');
        }
        
        return formatted;
    }

    addMessage(content, type, isHtml = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        if (type === 'user') {
            contentDiv.innerHTML = `<strong>👤 You:</strong><p>${this.escapeHtml(content)}</p>`;
        } else {
            contentDiv.innerHTML = `<strong>🤖 Assistant:</strong>`;
            if (isHtml) {
                contentDiv.innerHTML += this.formatMarkdown(content);
            } else {
                contentDiv.innerHTML += `<p>${content}</p>`;
            }
        }
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        return messageDiv.id = `msg-${Date.now()}`;
    }

    addLoadingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant loading';
        messageDiv.id = `loading-${Date.now()}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <strong>🤖 Assistant:</strong>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        return messageDiv.id;
    }

    removeMessage(messageId) {
        const message = document.getElementById(messageId);
        if (message) {
            message.remove();
        }
    }

    formatMarkdown(text) {
        // Simple markdown formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>')
            .replace(/(\d+)\.\s+(.+?)(?=\n|$)/g, '<li>$2</li>')
            .replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>')
            .replace(/<\/li><li>/g, '</li><li>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chat application
document.addEventListener('DOMContentLoaded', () => {
    window.strunzChat = new StrunzKnowledgeChat();
});