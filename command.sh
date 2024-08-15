#!/bin/bash

# Function to escape special characters in a string
escape_special_chars() {
  echo "$1" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g'
}

# Function to send the shell command
send_shell_command() {
  echo "Enter the shell command you want to execute:"
  read shell_command
  escaped_command=$(escape_special_chars "$shell_command")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"shell\", \"command\": \"$escaped_command\"}"
}

# Function to send the module command
send_module_command() {
  echo "Enter the module name you want to execute:"
  read module_name
  escaped_module=$(escape_special_chars "$module_name")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"module\", \"module\": \"$escaped_module\"}"
}

# Main script
echo "Do you want to run a shell command or a module?"
echo "Type 'shell' for shell command or 'module' for module:"
read choice

if [ "$choice" = "shell" ]; then
  send_shell_command
elif [ "$choice" = "module" ]; then
  send_module_command
else
  echo "Invalid choice. Please run the script again and choose either 'shell' or 'module'."
fi

