# Gemini API Setup Guide

## Overview
This guide explains how to set up Google Gemini API for the StrunzKnowledge MCP Server's auth-less client integration.

## Prerequisites
- Google Cloud account
- Google AI Studio access
- Valid billing account (API has free tier)

## Step 1: Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Select your Google Cloud project or create a new one
4. Copy the generated API key

## Step 2: Enable Required APIs

The error `API_KEY_SERVICE_BLOCKED` indicates the Generative Language API needs to be enabled.

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Generative Language API"
5. Click on it and press "Enable"

Alternative method using gcloud CLI:
```bash
gcloud services enable generativelanguage.googleapis.com
```

## Step 3: Configure Environment

### Local Development
Add to your `.env` file:
```env
GOOGLE_GEMINI_API_KEY=your-api-key-here
```

### Railway Deployment
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Variables" tab
4. Add new variable:
   - Name: `GOOGLE_GEMINI_API_KEY`
   - Value: Your API key

## Step 4: Verify Setup

Run the test script:
```bash
python src/tests/test_gemini_integration.py
```

Expected output:
```
✅ API key found: AIzaSy...
✅ API key is valid and working
✅ Enhanced search completed
✅ Tools registered successfully
```

## Step 5: Available Gemini Tools

Once configured, these enhanced MCP tools become available:

### 1. `search_knowledge_gemini`
Intelligent search with LLM-powered synthesis of results.

### 2. `ask_strunz_gemini`
Direct Q&A about Dr. Strunz's health philosophy with personalized answers.

### 3. `analyze_health_topic_gemini`
Comprehensive analysis of health topics from multiple perspectives.

### 4. `validate_gemini_connection`
Test tool to verify Gemini API connectivity.

## Troubleshooting

### Error: API_KEY_SERVICE_BLOCKED
- Enable the Generative Language API in Google Cloud Console
- Ensure your project has billing enabled (free tier available)
- Wait 5-10 minutes after enabling for changes to propagate

### Error: 403 Permission Denied
- Check API key is correct
- Verify project has necessary permissions
- Ensure API is enabled for your project

### Error: Invalid API Key
- Regenerate key in Google AI Studio
- Check for extra spaces or characters
- Ensure key is properly quoted in .env file

## Security Considerations

1. **Never commit API keys**: Ensure `.env` is in `.gitignore`
2. **Use environment variables**: Always load from environment
3. **Rotate keys regularly**: Generate new keys periodically
4. **Monitor usage**: Check Google Cloud Console for usage patterns
5. **Set quotas**: Configure spending limits in Google Cloud

## Auth-less Client Architecture

The Gemini integration enables auth-less client functionality:

1. **Browser Extension**: Uses only Gemini API key
2. **No Server Auth**: Direct API calls from client
3. **Privacy First**: All processing in browser
4. **Simple Setup**: Just one API key needed

## API Limits and Quotas

Free tier includes:
- 60 requests per minute
- 1,000,000 tokens per month
- No charge for first tier
- Model: gemini-2.5-flash (latest and fastest)

Monitor usage:
- Google Cloud Console > APIs & Services > Credentials
- Check "Metrics" tab for usage statistics

## Next Steps

1. Test enhanced tools in Claude.ai interface
2. Monitor API usage and costs
3. Implement rate limiting if needed
4. Consider caching for common queries
5. Plan browser extension development

## Support

For issues:
- Check [Google AI Studio Documentation](https://ai.google.dev/docs)
- Review [API Error Codes](https://ai.google.dev/api/rest/v1/TopLevel/generateContent#errors)
- Open GitHub issue with error details