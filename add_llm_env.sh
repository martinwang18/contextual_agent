#!/bin/bash
# Helper script to add LLM environment variables to .env file

ENV_FILE="config/.env"

echo "=========================================="
echo "LLM Environment Variables Setup"
echo "=========================================="
echo

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: $ENV_FILE not found!"
    exit 1
fi

echo "Current LLM-related environment variables in $ENV_FILE:"
echo
grep -E "PORTKEY|OPENAI" "$ENV_FILE" || echo "(None found)"
echo

# Check what's missing
PORTKEY_EXISTS=$(grep -c "^PORTKEY_API_KEY=" "$ENV_FILE" || echo 0)
OPENAI_VIRTUAL_EXISTS=$(grep -c "^OPENAI_VIRTUAL_KEY=" "$ENV_FILE" || echo 0)
OPENAI_API_EXISTS=$(grep -c "^OPENAI_API_KEY=" "$ENV_FILE" || echo 0)

echo "Status:"
echo "  PORTKEY_API_KEY: $([ $PORTKEY_EXISTS -gt 0 ] && echo '✓ Found' || echo '✗ Missing')"
echo "  OPENAI_VIRTUAL_KEY: $([ $OPENAI_VIRTUAL_EXISTS -gt 0 ] && echo '✓ Found' || echo '✗ Missing')"
echo "  OPENAI_API_KEY: $([ $OPENAI_API_EXISTS -gt 0 ] && echo '✓ Found' || echo '✗ Missing')"
echo

# Offer to add missing variables
if [ $PORTKEY_EXISTS -eq 0 ] || ([ $OPENAI_VIRTUAL_EXISTS -eq 0 ] && [ $OPENAI_API_EXISTS -eq 0 ]); then
    echo "Would you like to add the missing variables? (y/n)"
    read -r response

    if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
        echo

        # Add Portkey API Key
        if [ $PORTKEY_EXISTS -eq 0 ]; then
            echo "Enter your PORTKEY_API_KEY:"
            read -r portkey_key
            if [ -n "$portkey_key" ]; then
                echo "" >> "$ENV_FILE"
                echo "# Portkey Gateway" >> "$ENV_FILE"
                echo "PORTKEY_API_KEY=$portkey_key" >> "$ENV_FILE"
                echo "✓ Added PORTKEY_API_KEY"
            fi
        fi

        # Add OpenAI Virtual Key
        if [ $OPENAI_VIRTUAL_EXISTS -eq 0 ] && [ $OPENAI_API_EXISTS -eq 0 ]; then
            echo
            echo "Enter your OPENAI_VIRTUAL_KEY (or press Enter to skip and use direct API key):"
            read -r openai_virtual_key

            if [ -n "$openai_virtual_key" ]; then
                echo "OPENAI_VIRTUAL_KEY=$openai_virtual_key" >> "$ENV_FILE"
                echo "✓ Added OPENAI_VIRTUAL_KEY"
            else
                echo
                echo "Enter your OPENAI_API_KEY (optional):"
                read -r openai_api_key
                if [ -n "$openai_api_key" ]; then
                    echo "OPENAI_API_KEY=$openai_api_key" >> "$ENV_FILE"
                    echo "✓ Added OPENAI_API_KEY"
                fi
            fi
        fi

        echo
        echo "=========================================="
        echo "✅ Environment variables updated!"
        echo "=========================================="
        echo
        echo "Next steps:"
        echo "1. Restart your application: ./run.sh"
        echo "2. Test LLM connection: source venv/bin/activate && python test_llm.py"
        echo
    else
        echo "Skipped. You can manually edit $ENV_FILE"
    fi
else
    echo "✅ All required environment variables are present!"
    echo
    echo "To test the LLM connection, run:"
    echo "  source venv/bin/activate && python test_llm.py"
fi
