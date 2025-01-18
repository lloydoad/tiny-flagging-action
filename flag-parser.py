#!/usr/bin/env python3
import sys
import json
import re
import glob
import argparse
from pathlib import Path
from typing import Dict, List, Union
from dataclasses import dataclass

@dataclass
class FeatureFlag:
    key: str
    default_value: Union[str, bool]
    type: str

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

def find_flag_files(search_pattern: str) -> List[Path]:
    return [Path(f) for f in glob.glob(search_pattern, recursive=True)]

def main():
    parser = argparse.ArgumentParser(description='Parse Swift Feature Flag files')
    parser.add_argument('pattern', help='Search pattern for Swift files (e.g. "**/*FeatureFlag.swift")')
    parser.add_argument('--output', '-o', help='Output JSON file')
    args = parser.parse_args()

    all_flags = {}
    flag_files = find_flag_files(args.pattern)
    
    if not flag_files:
        print(f"No files found matching pattern: {args.pattern}", file=sys.stderr)
        sys.exit(1)
    
    for path in flag_files:
        try:
            content = path.read_text()
            enum_name = path.stem
            flag_parser = FlagParser(content)
            flags = flag_parser.parse()
            all_flags[enum_name] = [vars(flag) for flag in flags]
        except Exception as e:
            print(f"Error parsing {path}: {e}", file=sys.stderr)
            continue
    
    output = json.dumps(all_flags, indent=2)
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)

if __name__ == '__main__':
    main()