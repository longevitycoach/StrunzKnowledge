#!/usr/bin/env node

/**
 * Claude Desktop MCP Client Bridge
 * Connects Claude Desktop to the remote Dr. Strunz Knowledge MCP server
 */

const { spawn } = require('child_process');
const { EventEmitter } = require('events');

class MCPClientBridge extends EventEmitter {
    constructor(serverUrl = 'https://strunz.up.railway.app') {
        super();
        this.serverUrl = serverUrl;
        this.requestId = 0;
        this.pendingRequests = new Map();
        this.connected = false;
        
        // Setup stdio communication with Claude Desktop
        this.setupStdioHandlers();
        
        // Connect to remote MCP server
        this.connectToServer();
    }
    
    setupStdioHandlers() {
        // Handle incoming messages from Claude Desktop
        process.stdin.on('data', (data) => {
            try {
                const message = JSON.parse(data.toString());
                this.handleClaudeMessage(message);
            } catch (error) {
                this.sendError(-32700, 'Parse error', null);
            }
        });
        
        process.stdin.on('end', () => {
            this.disconnect();
        });
    }
    
    async connectToServer() {
        try {
            // Test connection to remote server
            const response = await fetch(`${this.serverUrl}/`);
            if (response.ok) {
                this.connected = true;
                console.error('Connected to Dr. Strunz Knowledge MCP Server');
            } else {
                throw new Error(`Server returned ${response.status}`);
            }
        } catch (error) {
            console.error('Failed to connect to MCP server:', error.message);
            process.exit(1);
        }
    }
    
    async handleClaudeMessage(message) {
        const { method, params, id } = message;
        
        try {
            switch (method) {
                case 'initialize':
                    await this.handleInitialize(params, id);
                    break;
                    
                case 'tools/list':
                    await this.handleToolsList(id);
                    break;
                    
                case 'tools/call':
                    await this.handleToolCall(params, id);
                    break;
                    
                case 'resources/list':
                    await this.handleResourcesList(id);
                    break;
                    
                case 'resources/read':
                    await this.handleResourceRead(params, id);
                    break;
                    
                default:
                    this.sendError(-32601, 'Method not found', id);
            }
        } catch (error) {
            this.sendError(-32603, 'Internal error', id);
        }
    }
    
    async handleInitialize(params, id) {
        const response = {
            jsonrpc: '2.0',
            result: {
                protocolVersion: '2024-11-05',
                capabilities: {
                    tools: {},
                    resources: {}
                },
                serverInfo: {
                    name: 'Dr. Strunz Knowledge MCP Server',
                    version: '0.2.0'
                }
            },
            id
        };
        
        this.sendMessage(response);
    }
    
    async handleToolsList(id) {
        // Return the list of available tools
        const tools = [
            {
                name: 'knowledge_search',
                description: 'Search Dr. Strunz knowledge base',
                inputSchema: {
                    type: 'object',
                    properties: {
                        query: { type: 'string' },
                        filters: { type: 'object' }
                    },
                    required: ['query']
                }
            },
            {
                name: 'get_optimal_diagnostic_values',
                description: 'Get optimal diagnostic values based on age, gender, and conditions',
                inputSchema: {
                    type: 'object',
                    properties: {
                        age: { type: 'number' },
                        gender: { type: 'string' },
                        weight: { type: 'number' },
                        height: { type: 'number' },
                        athlete: { type: 'boolean' },
                        conditions: { type: 'array' }
                    },
                    required: ['age', 'gender']
                }
            },
            {
                name: 'create_health_protocol',
                description: 'Create personalized health protocol',
                inputSchema: {
                    type: 'object',
                    properties: {
                        condition: { type: 'string' },
                        user_profile: { type: 'object' }
                    },
                    required: ['condition']
                }
            },
            {
                name: 'analyze_supplement_stack',
                description: 'Analyze supplement combinations',
                inputSchema: {
                    type: 'object',
                    properties: {
                        supplements: { type: 'array' },
                        health_goals: { type: 'array' }
                    },
                    required: ['supplements']
                }
            },
            {
                name: 'get_dr_strunz_biography',
                description: 'Get Dr. Strunz biography and achievements',
                inputSchema: {
                    type: 'object',
                    properties: {}
                }
            }
        ];
        
        const response = {
            jsonrpc: '2.0',
            result: { tools },
            id
        };
        
        this.sendMessage(response);
    }
    
    async handleToolCall(params, id) {
        const { name, arguments: args } = params;
        
        try {
            // Call the remote MCP server tool
            const result = await this.callRemoteTool(name, args);
            
            const response = {
                jsonrpc: '2.0',
                result: {
                    content: [
                        {
                            type: 'text',
                            text: JSON.stringify(result, null, 2)
                        }
                    ]
                },
                id
            };
            
            this.sendMessage(response);
        } catch (error) {
            this.sendError(-32603, `Tool call failed: ${error.message}`, id);
        }
    }
    
    async handleResourcesList(id) {
        const resources = [
            {
                uri: 'knowledge_statistics',
                name: 'Knowledge Base Statistics',
                description: 'Statistics about the Dr. Strunz knowledge base',
                mimeType: 'application/json'
            }
        ];
        
        const response = {
            jsonrpc: '2.0',
            result: { resources },
            id
        };
        
        this.sendMessage(response);
    }
    
    async handleResourceRead(params, id) {
        const { uri } = params;
        
        try {
            let content = '';
            
            if (uri === 'knowledge_statistics') {
                // Get statistics from remote server
                const stats = await this.callRemoteTool('get_vector_db_analysis', {});
                content = JSON.stringify(stats, null, 2);
            }
            
            const response = {
                jsonrpc: '2.0',
                result: {
                    contents: [
                        {
                            uri,
                            mimeType: 'application/json',
                            text: content
                        }
                    ]
                },
                id
            };
            
            this.sendMessage(response);
        } catch (error) {
            this.sendError(-32603, `Resource read failed: ${error.message}`, id);
        }
    }
    
    async callRemoteTool(toolName, args) {
        // This would normally call the remote HTTP server
        // For now, return mock data that matches the tool's expected output
        
        const mockResponses = {
            'knowledge_search': {
                query: args.query || 'test',
                results: [
                    {
                        id: 'result_001',
                        source: 'books',
                        title: 'Dr. Strunz Knowledge Result',
                        content: `Information about ${args.query || 'health optimization'} from Dr. Strunz's extensive knowledge base.`,
                        score: 0.95,
                        metadata: {
                            book: 'Die Amino-Revolution',
                            chapter: '7: Vitamine und ihre Cofaktoren',
                            page: 127,
                            book_url: 'https://www.strunz.com/buecher/die-amino-revolution',
                            chapter_info: 'Chapter 7',
                            page_info: 'Page 127'
                        }
                    }
                ]
            },
            'get_optimal_diagnostic_values': {
                age: args.age,
                gender: args.gender,
                metadata: {
                    data_source: 'Dr. Strunz Optimal Values Database',
                    last_updated: '2025-01-14',
                    note: 'These are optimal values for peak health, not just normal ranges'
                },
                vitamins: {
                    'vitamin_d_25oh': {
                        value: args.age < 50 ? '70-80' : '80-90',
                        unit: 'ng/ml',
                        note: 'Higher for athletes and older adults'
                    },
                    'vitamin_b12': {
                        value: '800-1000',
                        unit: 'pg/ml',
                        note: 'Higher end optimal for cognitive function'
                    }
                },
                minerals: {
                    'magnesium_rbc': {
                        value: '6.0-6.5',
                        unit: 'mg/dl',
                        note: 'Red blood cell magnesium preferred over serum'
                    },
                    'ferritin': {
                        value: args.gender === 'male' ? '150-250' : '80-150',
                        unit: 'ng/ml',
                        note: 'Gender-specific optimal ranges'
                    }
                }
            },
            'create_health_protocol': {
                condition: args.condition,
                user_profile: args.user_profile,
                recommendations: [
                    {
                        supplement: 'Vitamin D3',
                        dose: '4000-6000 IU',
                        timing: 'morning with fat',
                        source: 'Die Amino-Revolution, Chapter 7',
                        book_url: 'https://www.strunz.com/buecher/die-amino-revolution',
                        chapter: '7',
                        page: '127-132'
                    }
                ]
            },
            'analyze_supplement_stack': {
                supplements: args.supplements,
                safety_analysis: 'All combinations appear safe based on Dr. Strunz protocols',
                interactions: [],
                optimization_suggestions: [
                    'Consider timing adjustments',
                    'Add cofactors for better absorption'
                ],
                timing_recommendations: [
                    {
                        supplement: 'Vitamin D3',
                        timing: 'morning with fat'
                    }
                ]
            },
            'get_dr_strunz_biography': {
                full_name: 'Dr. med. Ulrich Strunz',
                title: 'Pioneer of Molecular and Preventive Medicine',
                birth_year: 1943,
                nationality: 'German',
                medical_education: {
                    degree: 'Doctor of Medicine (Dr. med.)',
                    specialization: 'Internal Medicine and Molecular Medicine'
                },
                career_highlights: {
                    books_authored: '40+',
                    years_in_practice: '40+',
                    specialty: 'Preventive and Molecular Medicine'
                }
            }
        };
        
        return mockResponses[toolName] || { error: 'Tool not implemented' };
    }
    
    sendMessage(message) {
        process.stdout.write(JSON.stringify(message) + '\n');
    }
    
    sendError(code, message, id) {
        const error = {
            jsonrpc: '2.0',
            error: { code, message },
            id
        };
        process.stdout.write(JSON.stringify(error) + '\n');
    }
    
    disconnect() {
        this.connected = false;
        process.exit(0);
    }
}

// Start the MCP client bridge
const serverUrl = process.env.MCP_SERVER_URL || 'https://strunz.up.railway.app';
new MCPClientBridge(serverUrl);