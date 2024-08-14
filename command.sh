#!/bin/bash

# Set the Node.js server URL
NODE_SERVER_URL="http://10.0.100.100:3000"

# Function to prompt user for command type
function send_command() {
    echo "Choose the command type:"
    echo "1) Shell Command"
    echo "2) Python Module"
    echo "3) C Module"
    read -p "Enter the number: " command_type

    case $command_type in
        1)
            read -p "Enter the shell command to execute: " shell_command
            curl -X POST "$NODE_SERVER_URL/send-command" \
            -H "Content-Type: application/json" \
            -d "{\"type\": \"shell\", \"command\": \"$shell_command\"}"
            ;;
        2)
            read -p "Enter the Python module to execute: " module_name
            curl -X POST "$NODE_SERVER_URL/send-command" \
            -H "Content-Type: application/json" \
            -d "{\"type\": \"module\", \"module\": \"$module_name\"}"
            ;;
        3)
            read -p "Enter the C module to execute: " c_module_name
            curl -X POST "$NODE_SERVER_URL/send-command" \
            -H "Content-Type: application/json" \
            -d "{\"type\": \"c_module\", \"module\": \"$c_module_name\"}"
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
}

# Run the function to prompt user for input
send_command

