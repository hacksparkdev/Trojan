#!/bin/bash# Function to escape special characters in a stringescape_special_chars() {
  echo"$1" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g'
}

# Function to send the shell commandsend_shell_command() {
  echo"Enter the shell command you want to execute:"read shell_command
  escaped_command=$(escape_special_chars "$shell_command")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"shell\", \"command\": \"$escaped_command\"}"
}

# Function to send the module commandsend_module_command() {
  echo"Enter the module name you want to execute:"read module_name
  escaped_module=$(escape_special_chars "$module_name")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"module\", \"module\": \"$escaped_module\"}"
}

# Function to send the C module commandsend_c_module_command() {
  echo"Enter the C module name you want to execute:"read c_module_name
  escaped_c_module=$(escape_special_chars "$c_module_name")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"c_module\", \"module\": \"$escaped_c_module\"}"
}

# Main scriptecho"Do you want to run a shell command, a module, or a C module?"echo"Type 'shell' for shell command, 'module' for Python module, or 'c_module' for C module:"read choice

if [ "$choice" = "shell" ]; then
  send_shell_command
elif [ "$choice" = "module" ]; then
  send_module_command
elif [ "$choice" = "c_module" ]; then
  send_c_module_command
elseecho"Invalid choice. Please run the script again and choose either 'shell', 'module', or 'c_module'."fi
