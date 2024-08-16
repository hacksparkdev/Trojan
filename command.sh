# Function to send the C module command
send_c_module_command() {
  echo "Enter the C module name you want to execute:"
  read c_module_name
  escaped_c_module=$(escape_special_chars "$c_module_name")
  curl -X POST http://10.0.100.100:3000/send-command \
    -H "Content-Type: application/json" \
    -d "{\"type\": \"c_module\", \"module\": \"$escaped_c_module\"}"
}

# Main script
echo "Do you want to run a shell command, a module, or a C module?"
echo "Type 'shell' for shell command, 'module' for Python module, or 'c_module' for C module:"
read choice

if [ "$choice" = "shell" ]; then
  send_shell_command
elif [ "$choice" = "module" ]; then
  send_module_command
elif [ "$choice" = "c_module" ]; then
  send_c_module_command
else
  echo "Invalid choice. Please run the script again and choose either 'shell', 'module', or 'c_module'."
fi

