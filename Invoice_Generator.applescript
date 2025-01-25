tell application "Terminal"
    -- Get the absolute path to the project directory
    set projectDir to "/Users/williamvansickleiii/code/PraisonAI/0-lite-llm-agents"
    
    -- Create a new terminal window and execute the script
    do script "cd " & quoted form of projectDir & " && ./start_app.sh"
    activate
end tell 