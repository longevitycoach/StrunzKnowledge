/**
 * StrunzKnowledge Chat Frontend
 * Auth-less client using Gemini API for intelligent health insights
 */

class StrunzKnowledgeChat {
    constructor() {
        // Use localhost for development, Railway URL for production
        this.mcpServerUrl = window.location.hostname === 'localhost' 
            ? 'http://localhost:8000' 
            : 'https://strunz.up.railway.app';
        this.isConnected = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.checkMCPServer();
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
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });
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
                    
                    // Auto-connect if server has Gemini configured
                    if (data.gemini_integration.server_side_key) {
                        this.connectToServer();
                    }
                }
            }
        } catch (error) {
            this.mcpStatus.textContent = '❌ Offline';
            this.mcpStatus.style.color = '#e53e3e';
        }
    }

    connectToServer() {
        this.isConnected = true;
        this.setupPanel.style.display = 'none';
        this.chatContainer.style.display = 'flex';
        this.chatInput.disabled = false;
        this.sendBtn.disabled = false;
        this.statusText.textContent = '🟢 Connected';
        this.statusText.classList.add('connected');
        this.chatInput.focus();
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
            this.addMessage(error.message || 'Sorry, I encountered an error. Please try again.', 'assistant');
            console.error('Chat error:', error);
        }
    }

    async searchKnowledge(query) {
        const prompt = `
As an expert on Dr. Ulrich Strunz's health and nutrition knowledge, search for information about: "${query}"

Provide relevant findings from Dr. Strunz's work, including:
1. Key insights and recommendations
2. Scientific backing if available
3. Practical applications
4. Specific vitamins, minerals, or supplements mentioned

Format your response in a clear, helpful way.`;

        return await this.callServerGemini(prompt, 'search');
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

        return await this.callServerGemini(prompt, 'ask');
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

        return await this.callServerGemini(prompt, 'analyze');
    }

    async callServerGemini(prompt, toolType) {
        try {
            const response = await fetch(`${this.mcpServerUrl}/api/gemini/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt: prompt,
                    tool_type: toolType,
                    temperature: 0.7,
                    max_tokens: 2048
                })
            });

            if (!response.ok) {
                const error = await response.json();
                if (response.status === 429) {
                    throw new Error(`Rate limit exceeded: ${error.detail.message}. Please try again in ${error.detail.retry_after} seconds.`);
                }
                throw new Error(`Server error: ${error.detail || response.statusText}`);
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Server Gemini error:', error);
            throw error;
        }
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
        // Enhanced markdown to HTML conversion
        let html = text;
        
        // Headers
        html = html.replace(/^### (.*?)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*?)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*?)$/gm, '<h1>$1</h1>');
        
        // Bold and italic
        html = html.replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Lists - handle numbered lists
        html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');
        // Wrap consecutive <li> tags in <ol>
        html = html.replace(/(<li>.*?<\/li>\n?)+/g, function(match) {
            return '<ol>' + match + '</ol>';
        });
        
        // Lists - handle bullet points
        html = html.replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>');
        // Wrap consecutive <li> tags that aren't in <ol> in <ul>
        html = html.replace(/(<li>(?!.*<ol>).*?<\/li>\n?)+/g, function(match) {
            if (!match.includes('<ol>')) {
                return '<ul>' + match + '</ul>';
            }
            return match;
        });
        
        // Paragraphs
        html = html.split('\n\n').map(para => {
            // Don't wrap headers, lists, or already wrapped content
            if (para.match(/^<[houl]/i) || para.trim() === '') {
                return para;
            }
            return '<p>' + para.replace(/\n/g, '<br>') + '</p>';
        }).join('\n');
        
        // Clean up
        html = html.replace(/<p><\/p>/g, '');
        html = html.replace(/<p>(<[houl])/gi, '$1');
        html = html.replace(/(<\/[houl]>)<\/p>/gi, '$1');
        
        return html;
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