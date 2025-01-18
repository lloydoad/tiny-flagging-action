import json
import argparse
import sys

def python_to_js_value(value):
    if value is None:
        return 'null'
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)

def generate_html(template_path, output_path, flags_path, flags_json_repo):
    with open(output_path + '/' + flags_path) as f:
        flags = json.load(f)

    replacements = {
        '{FLAG_JSON_DATA}': flags,
        '{FLAG_PATH}': flags_path,
        '{OUTPUT_PATH}': output_path,
        '{FLAG_JSON_REPO}': flags_json_repo
    }

    with open(template_path) as f:
        template = f.read()
    
    rendered = template
    for key, value in replacements.items():
        js_value = python_to_js_value(value)
        rendered = rendered.replace(key, js_value)
    
    with open(output_path + '/index.html', 'w') as f:
        f.write(rendered)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate HTML from template with feature flags')
    parser.add_argument('--input', required=True, help='Path to template HTML file')
    parser.add_argument('--output', required=True, help='Path for output index.html file')
    parser.add_argument('--flags', required=True, help='Path to flags JSON file')
    parser.add_argument('--repo', required=True, help='GitHub repository name')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    
    generate_html(args.input, args.output, args.flags, args.repo)