#!/usr/bin/env python3
import sys, json, re, glob, argparse, os
from pathlib import Path
from typing import Dict, List, Union
from dataclasses import dataclass

@dataclass
class FeatureFlag:
    key: str
    default_value: Union[str, bool]
    type: str
    override_value: Union[str, bool, None] = None

class FlagParser:
    def __init__(self, content: str):
        self.content = content
        self.is_string = 'defaultValue: String' in content
        self.is_bool = 'defaultValue: Bool' in content
        self.flag_type = 'string' if self.is_string else 'bool'
        
    def parse_cases(self) -> set:
        case_pattern = r'case\s+(\w+)(?:,|\n|\r\n|$)'
        return {match.group(1) for match in re.finditer(case_pattern, self.content)}
        
    def parse_default_values(self) -> Dict[str, Union[str, bool]]:
        switch_block = re.search(r'var\s+defaultValue:.*?{(.*?)}', self.content, re.DOTALL)
        if not switch_block:
            return {}
            
        value_map = {}
        case_pattern = r'case\s+\.([^:]+):\s*(?:return\s+)?(\w+|\"[^\"]+\")'
        
        for match in re.finditer(case_pattern, switch_block.group(1)):
            case_names = [c.strip().replace('.', '') for c in match.group(1).split(',')]
            value = match.group(2)
            
            parsed_value = value.strip('"') if self.is_string else (value == 'true')
            for case_name in case_names:
                value_map[case_name.strip()] = parsed_value
                
        return value_map

    def parse(self) -> List[FeatureFlag]:
        cases = self.parse_cases()
        default_values = self.parse_default_values()
        
        return [
            FeatureFlag(
                key=case,
                default_value=default_values.get(case),
                type=self.flag_type
            )
            for case in cases
            if case in default_values
        ]

def find_flag_files(pattern: str) -> List[Path]:
    return [Path(f) for f in glob.glob(pattern, recursive=True)]

def merge_with_existing(new_flags: Dict[str, List[FeatureFlag]], existing_path: Path) -> Dict:
    try:
        if existing_path.exists():
            existing = json.loads(existing_path.read_text())
            
            # Create a map of existing overrides for each enum and key
            existing_overrides = {}
            for enum_name, flags in existing.items():
                existing_overrides[enum_name] = {
                    flag['key']: flag.get('override_value')
                    for flag in flags
                    if flag.get('override_value') is not None  # Only keep non-null overrides
                }
            
            # Apply existing overrides to new flags
            result = {}
            for enum_name, flags in new_flags.items():
                enum_overrides = existing_overrides.get(enum_name, {})
                result[enum_name] = [
                    {
                        'key': flag.key,
                        'default_value': flag.default_value,
                        'type': flag.type,
                        'override_value': enum_overrides.get(flag.key, flag.override_value)
                    }
                    for flag in flags
                ]
            return result
            
        return {enum_name: [vars(flag) for flag in flags] 
               for enum_name, flags in new_flags.items()}
                
    except Exception as e:
        print(f"Error reading existing flags: {e}")
        return {enum_name: [vars(flag) for flag in flags] 
               for enum_name, flags in new_flags.items()}

def create_flag_directories(flags_data: Dict, output_dir: str) -> None:
    # Create parent feature_flags directory
    feature_flags_dir = output_dir
    if os.path.exists(feature_flags_dir):
        # Clean up existing directories and files
        for item in os.listdir(feature_flags_dir):
            item_path = os.path.join(feature_flags_dir, item)
            if os.path.isdir(item_path):
                # Clean up directory contents
                for file in os.listdir(item_path):
                    print(file)
                    os.remove(os.path.join(item_path, file))
                os.rmdir(item_path)
            else:
                # Remove files
                os.remove(item_path)
        os.rmdir(feature_flags_dir)
    
    # Create new directories and files
    os.makedirs(feature_flags_dir)
    for enum_name, flags in flags_data.items():
        enum_dir = os.path.join(feature_flags_dir, enum_name)
        os.makedirs(enum_dir, exist_ok=True)
        
        for flag in flags:
            # Handle dictionary format instead of FeatureFlag object
            value = flag['override_value'] if flag['override_value'] is not None else flag['default_value']
            # Convert boolean/string to string representation
            value_str = str(value).lower() if isinstance(value, bool) else str(value)
            
            # Create file with the flag's value
            flag_path = os.path.join(enum_dir, flag['key'])
            with open(flag_path, 'w') as f:
                f.write(value_str)

def main():
    parser = argparse.ArgumentParser(description='Parse Swift Feature Flag files')
    parser.add_argument('input_dir', help='Directory to search for Swift files')
    parser.add_argument('output_dir', help='Directory to output processed flags')
    parser.add_argument('pattern', help='Search pattern for Swift files')
    args = parser.parse_args()
    
    all_flags = {}
    # Use input_dir and pattern to find files
    flag_files = find_flag_files(os.path.join(args.input_dir, args.pattern))
    
    if not flag_files:
        print(f"No files found matching pattern: {args.pattern} in directory: {args.input_dir}")
        sys.exit(1)
    
    for path in flag_files:
        try:
            content = path.read_text()
            enum_name = path.stem
            flag_parser = FlagParser(content)
            flags = flag_parser.parse()
            all_flags[enum_name] = flags
        except Exception as e:
            print(f"Error parsing {path}: {e}")
            continue
    
    # First merge with existing flags.json
    output_path = Path(os.path.join(args.output_dir, "flags.json"))
    merged = merge_with_existing(all_flags, output_path)
    
    # Then clean up and create directories with merged data
    create_flag_directories(merged, args.output_dir)
    
    # Finally write the merged flags.json
    output_path.write_text(json.dumps(merged, indent=2))

if __name__ == '__main__':
    main()