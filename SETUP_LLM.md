# LLM Setup Guide

## Current Status
✅ Code structure is correct and working
✅ Fallback behavior functions properly
❌ Missing environment variables for LLM integration

## Required Environment Variables

Add these to your `config/.env` file:

```bash
# Portkey Gateway Configuration
PORTKEY_API_KEY=your_portkey_api_key_here

# Option 1: Use Portkey Virtual Key (Recommended)
OPENAI_VIRTUAL_KEY=your_openai_virtual_key_here

# Option 2: Use Direct OpenAI API Key (Alternative)
# OPENAI_API_KEY=your_openai_api_key_here
```

## Setup Steps

1. **Open your `.env` file:**
   ```bash
   nano config/.env
   # or
   code config/.env
   ```

2. **Add the required variables:**
   - `PORTKEY_API_KEY`: Your Portkey API key
   - `OPENAI_VIRTUAL_KEY`: Your OpenAI virtual key from Portkey dashboard

3. **Save the file and restart the application:**
   ```bash
   # Stop the current server (Ctrl+C)
   ./run.sh
   ```

## Testing the Setup

Run the test script to verify:
```bash
source venv/bin/activate
python test_llm.py
```

If successful, you should see:
```
✅ All tests passed!
```

## Current Gateway Configuration

The application is configured to use:
- **Portkey Gateway URL**: `https://cybertron-service-gateway.doordash.team/v1`
- **LLM Model**: GPT-4 (via OpenAI)

## Troubleshooting

### Error: "No PORTKEY_API_KEY found"
- Make sure `PORTKEY_API_KEY` is set in `config/.env`
- Restart the application after adding it

### Error: "No OPENAI_VIRTUAL_KEY or OPENAI_API_KEY found"
- Add either `OPENAI_VIRTUAL_KEY` (recommended) or `OPENAI_API_KEY`
- The virtual key is managed through your Portkey dashboard

### Error: "attribute '__default__' of 'typing.ParamSpec' objects is not writable"
- This was a compatibility issue that has been fixed
- We upgraded `portkey-ai` to version 2.2.0
- If you still see this, run: `pip install --upgrade portkey-ai typing-extensions`

## What the LLM Does

When properly configured, the LLM (GPT-4) will:

1. **Analyze Context**: Examines holidays, weather, and news events
2. **Generate Recommendations**: Suggests 3-5 retail items relevant to the context
3. **Provide Reasoning**: Explains why these items were recommended as a group
4. **Individual Rationales**: Gives specific reasons for each recommended item

The UI will display a blue box with the robot icon (🤖) showing the LLM's overall reasoning.
