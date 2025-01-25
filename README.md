# Lite LLM Agents

This directory contains an implementation of PraisonAI agents using Claude 3.5 Sonnet for model inference.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables (optional):
- Create a `.env` file
- Add your API keys if needed:
```
ANTHROPIC_API_KEY=your_api_key_here
```

3. Run the agent:
```bash
python lite_llm_agent.py
```

## Configuration

The agent is configured with the following attributes:
- Role: Assistant
- Goal: Help users with their questions and tasks
- Memory: Enabled
- Delegation: Disabled
- Verbose: Enabled

LLM Configuration:
- Model: Claude 3.5 Sonnet
- Temperature: 0.7
- Top P: 0.9
- Max Tokens: 1000
- Presence Penalty: 0.1
- Frequency Penalty: 0.1

You can modify these settings in the `llm_config` dictionary in `lite_llm_agent.py`.

## Customization

To customize the agent's behavior:
1. Modify the agent's role, goal, and backstory
2. Adjust the LLM configuration parameters
3. Add additional tools or capabilities
4. Customize the conversation flow in the main() function

## Notes

- Make sure you have appropriate API access and keys set up for Claude 3.5 Sonnet
- The agent maintains memory of conversations by default
- Verbose mode is enabled for debugging purposes
- Consider adding error handling and logging for production use 