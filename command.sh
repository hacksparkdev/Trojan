#!/bin/bash

# Function to escape special characters in a string
escape_special_chars() {
  echo "$1" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g'
}

# Function to send a shell command
send_shell_command() {
  echo "Enter the shell command you want to execute:"
  read -r shell_command
  escaped_command=$(escape_special_chars "$shell_command")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"shell\", \"command\": \"$escaped_command\"}"
}

# Function to send a Python module command
send_module_command() {
  echo "Enter the Python module name you want to execute:"
  read -r module_name
  escaped_module=$(escape_special_chars "$module_name")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"module\", \"module\": \"$escaped_module\"}"
}

# Function to send a C module command
send_c_module_command() {
  echo "Enter the C module name you want to execute:"
  read -r c_module_name
  escaped_c_module=$(escape_special_chars "$c_module_name")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"c_module\", \"module\": \"$escaped_c_module\"}"
}

# Function to send a PowerShell command
send_powershell_command() {
  echo "Enter the PowerShell command you want to execute:"
  read -r powershell_command
  escaped_command=$(escape_special_chars "$powershell_command")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"powershell\", \"command\": \"$escaped_command\"}"
}

# Main script logic
echo "Choose a command type to execute:"
echo "1. Shell command"
echo "2. Python module"
echo "3. C module"
echo "4. PowerShell command"

read -r choice

case "$choice" in
  1)
    send_shell_command
    ;;
  2)
    send_module_command
    ;;
  3)
    send_c_module_command
    ;;
  4)
    send_powershell_command
    ;;
  *)
    echo "Invalid choice. Please choose a valid option."
    ;;
esac

