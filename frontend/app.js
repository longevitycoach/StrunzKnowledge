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
            console.log(`Checking MCP server at: ${this.mcpServerUrl}/health`);
            
            const response = await fetch(`${this.mcpServerUrl}/health`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
                mode: 'cors',
                timeout: 5000  // 5 second timeout
            });
            
            // Check if response is OK before trying to parse JSON
            if (!response.ok) {
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Health check response:', data);
            
            if (data.status === 'ok') {
                this.mcpStatus.textContent = '✅ Connected';
                this.mcpStatus.style.color = '#48bb78';
                
                // Auto-connect since server is available and has server-side Gemini key
                this.connectToServer();
                
                // Update status to show tools available
                if (data.tools_available) {
                    this.mcpStatus.textContent += ` (${data.tools_available} tools)`;
                }
            }
        } catch (error) {
            console.error('MCP Server connection error:', error);
            this.mcpStatus.textContent = '❌ Offline';
            this.mcpStatus.style.color = '#e53e3e';
            
            // Show more detailed error in console
            if (error.message.includes('Failed to fetch')) {
                console.error('CORS or network error. Make sure the server is running and CORS is enabled.');
            }
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

    async callMCPTool(toolName, args) {
        // For now, use direct API endpoints instead of MCP SSE
        // This will be more reliable until SSE is properly debugged
        
        try {
            switch (toolName) {
                case 'search_knowledge':
                    return await this.callDirectSearch(args.query, args.limit || 10);
                case 'analyze_health_topic':
                    return await this.callDirectAnalyze(args.topic);
                case 'create_health_protocol':
                    return await this.callDirectProtocol(args.condition);
                case 'analyze_forum_trends':
                    return await this.callDirectForum(args.topic);
                default:
                    throw new Error(`Tool ${toolName} not implemented yet`);
            }
        } catch (error) {
            console.error(`Direct tool call failed for ${toolName}:`, error);
            throw error;
        }
    }

    async callDirectSearch(query, limit) {
        // Call the search tool via REST API
        const response = await fetch(`${this.mcpServerUrl}/api/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, limit })
        });
        
        if (!response.ok) {
            throw new Error(`Search failed: ${response.status}`);
        }
        
        const result = await response.json();
        if (result.error) {
            throw new Error(result.error);
        }
        
        return result.content || 'No results found';
    }

    async callDirectAnalyze(topic) {
        // For now, use Gemini fallback
        const prompt = `Analyze "${topic}" from Dr. Strunz's knowledge base comprehensively.`;
        return await this.callServerGemini(prompt, 'analyze');
    }

    async callDirectProtocol(condition) {
        // For now, use Gemini fallback
        const prompt = `Create a health protocol for "${condition}" based on Dr. Strunz's recommendations.`;
        return await this.callServerGemini(prompt, 'ask');
    }

    async callDirectForum(topic) {
        // For now, use search fallback
        return await this.callDirectSearch(`forum ${topic}`, 10);
    }


    async sendMessage() {
        const message = this.chatInput.value.trim();
        if (!message || !this.isConnected) return;
        
        // Check for help command
        if (message.toLowerCase() === 'help' || message.toLowerCase() === '/help' || message.toLowerCase() === 'capabilities') {
            this.addMessage(message, 'user');
            this.chatInput.value = '';
            this.showCapabilities();
            return;
        }
        
        // Get selected tool
        const selectedTool = document.querySelector('input[name="tool"]:checked').value;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.chatInput.value = '';
        
        // Show loading message
        const loadingId = this.addLoadingMessage();
        
        try {
            let response;
            let capability;
            
            switch (selectedTool) {
                case 'search':
                    capability = '🔍 Search Knowledge';
                    response = await this.searchKnowledge(message);
                    break;
                case 'ask':
                    capability = '💊 Ask Dr. Strunz';
                    response = await this.askDrStrunz(message);
                    break;
                case 'analyze':
                    capability = '📊 Analyze Topic';
                    response = await this.analyzeHealthTopic(message);
                    break;
                default:
                    capability = '🔍 Search Knowledge';
                    response = await this.searchKnowledge(message);
            }
            
            // Remove loading message
            this.removeMessage(loadingId);
            
            // Add capability header to response
            const enhancedResponse = `<div class="capability-info">
                <strong>Capability Used:</strong> ${capability}<br>
                <strong>Knowledge Sources:</strong> Books, News Articles, Forum Discussions
            </div>
            <hr style="margin: 10px 0; border: none; border-top: 1px solid #e0e0e0;">
            ${response}`;
            
            // Add assistant response
            this.addMessage(enhancedResponse, 'assistant', true);
            
        } catch (error) {
            this.removeMessage(loadingId);
            this.addMessage(error.message || 'Sorry, I encountered an error. Please try again.', 'assistant');
            console.error('Chat error:', error);
        }
    }

    async searchKnowledge(query) {
        // Use Gemini API directly as primary method
        const forumKeywords = ['forum', 'diskutiert', 'gesprochen', 'community', 'diskussion', 'beiträge', 'posts'];
        const isForumQuery = forumKeywords.some(keyword => query.toLowerCase().includes(keyword));
            
            const prompt = isForumQuery ? `
Search the Dr. Strunz knowledge base SPECIFICALLY for FORUM discussions about: "${query}"

IMPORTANT: Focus on forum content and community discussions!

Please provide:
1. Relevant forum posts and discussions
2. Community experiences and user questions
3. How often the topic is discussed (if asked)
4. Different perspectives from forum members
5. Practical experiences shared by the community

Include metadata like post dates and authors when available.` : `
As an expert on Dr. Ulrich Strunz's health and nutrition knowledge, search for information about: "${query}"

Provide relevant findings from Dr. Strunz's work, including:
1. Key insights and recommendations
2. Scientific backing if available
3. Practical applications
4. Specific vitamins, minerals, or supplements mentioned

Search across books, news articles, and forum discussions.`;

        return await this.callServerGemini(prompt, 'search');
    }

    async askDrStrunz(question) {
        // Check if the question is asking about forum discussions or community topics
        const forumKeywords = ['forum', 'diskutiert', 'gesprochen', 'community', 'diskussion', 'beiträge', 'posts'];
        const isForumQuery = forumKeywords.some(keyword => question.toLowerCase().includes(keyword));
        
        if (isForumQuery) {
            // Use forum analysis tool for forum queries
            try {
                return await this.callMCPTool('analyze_forum_trends', { topic: question });
            } catch (error) {
                console.error('MCP tool call failed, falling back to search:', error);
                return await this.searchKnowledge(question);
            }
        }

        // Use Gemini API directly for health protocols
            const searchPrompt = `
Search the Dr. Strunz knowledge base specifically for FORUM discussions about: "${question}"

Focus on:
1. Forum posts and community discussions
2. User experiences and questions
3. Community insights and shared knowledge
4. Frequency of discussion if asked

Please search specifically in forum content and provide relevant forum discussions.`;
            
            return await this.callServerGemini(searchPrompt, 'search');
        }
        
        // Original ask prompt for non-forum questions
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
        // Use Gemini API directly for health topic analysis
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
                let errorMessage = `Server error: ${response.statusText}`;
                
                // Try to parse error details from JSON, but handle if it's not JSON
                try {
                    const error = await response.json();
                    if (response.status === 429 && error.detail) {
                        errorMessage = `Rate limit exceeded: ${error.detail.message}. Please try again in ${error.detail.retry_after} seconds.`;
                    } else if (error.detail) {
                        errorMessage = `Server error: ${error.detail}`;
                    }
                } catch (jsonError) {
                    // Response body is not JSON, use the default error message
                    console.warn('Failed to parse error response as JSON:', jsonError);
                }
                
                throw new Error(errorMessage);
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
    
    showCapabilities() {
        const capabilitiesInfo = `
<div class="capabilities-help" style="font-size: 0.95rem;">
    <h2 style="font-size: 1.3rem; margin-bottom: 12px;">📋 Help - Dr. Strunz Knowledge Assistant</h2>
    
    <p style="margin-bottom: 12px;"><strong>📚 Knowledge Base:</strong> 13 Books • 6,953 News Articles • 14,435 Forum Discussions</p>
    
    <p style="margin-bottom: 8px;"><strong>🛠️ Capabilities:</strong></p>
    <div style="margin-left: 0; margin-bottom: 12px; line-height: 1.6;">
        <div style="margin-bottom: 4px;">🔍 <strong>Search</strong> - Find information across all sources</div>
        <div style="margin-bottom: 4px;">💊 <strong>Ask Dr. Strunz</strong> - Get personalized health recommendations</div>
        <div style="margin-bottom: 4px;">📊 <strong>Analyze</strong> - Deep dive into any health topic</div>
        <div style="margin-bottom: 4px;">🧪 <strong>Stack Analysis</strong> - Optimize supplement combinations</div>
        <div style="margin-bottom: 4px;">🔄 <strong>Contradictions</strong> - Find evolving recommendations</div>
        <div style="margin-bottom: 4px;">📈 <strong>Evolution</strong> - Track topic changes over time</div>
        <div style="margin-bottom: 4px;">👨‍⚕️ <strong>Biography</strong> - Learn about Dr. Strunz</div>
    </div>
    
    <p style="margin-bottom: 8px;"><strong>💡 Quick Tips:</strong></p>
    <div style="margin-left: 15px; margin-bottom: 12px; line-height: 1.5;">
        <div style="margin-bottom: 3px;">• Select a tool below (Search/Ask/Analyze) before asking</div>
        <div style="margin-bottom: 3px;">• For forum discussions, include "forum" in your query</div>
        <div style="margin-bottom: 3px;">• Type <strong>help</strong> anytime to see this again</div>
    </div>
    
    <p style="margin-top: 12px; font-style: italic; font-size: 0.9rem;">✨ I'll show which capability I'm using and where the information comes from!</p>
</div>`;
        
        this.addMessage(capabilitiesInfo, 'assistant', true);
    }
}

// Initialize the chat application
document.addEventListener('DOMContentLoaded', () => {
    window.strunzChat = new StrunzKnowledgeChat();
});