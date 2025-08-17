// Debug version of showCapabilities to test
function testShowCapabilities() {
    console.log("testShowCapabilities called");
    
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
    
    console.log("Capabilities HTML:", capabilitiesInfo);
    return capabilitiesInfo;
}

// Test in console
console.log("Debug script loaded. Run testShowCapabilities() in console to see output.");