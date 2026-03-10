#!/usr/bin/env python3
"""APAR Parser - Extract IBM APAR information from web pages"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import requests
from bs4 import BeautifulSoup


class APARParser:
    BASE_URL = "https://www.ibm.com/support/pages/apar/"
    
    INFO_TYPES = {
        'type1': ['APAR Information'],
        'type2': ['Error description', 'Local fix', 'Problem summary', 
                  'Problem conclusion', 'Temporary fix', 'Comments', 'Modules/Macros'],
        'type3': ['Fix information', 'Applicable component levels'],
        'type4': ['APAR status']
    }

    def __init__(self, output_dir: Path, output_format: str = 'txt'):
        self.output_dir = output_dir
        self.output_format = output_format
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_apar(self, apar_number: str) -> Optional[str]:
        """Fetch APAR page content"""
        try:
            response = requests.get(f"{self.BASE_URL}{apar_number}", timeout=30)
            response.raise_for_status()
            return response.text.replace('<p/>', '')
        except requests.RequestException as e:
            print(f"Error fetching {apar_number}: {e}")
            return None

    def parse_apar(self, apar_number: str, html: str) -> tuple[str, str | dict]:
        """Parse APAR HTML and return status and content"""
        soup = BeautifulSoup(html, 'html.parser')
        
        if not soup.title:
            return 'logon', html
        
        if apar_number not in soup.title.text:
            return 'notfound', html
        
        if self.output_format == 'json':
            content = self._extract_json(soup, apar_number)
        else:
            content = self._extract_content(soup, apar_number)
        
        return 'success', content

    def _extract_content(self, soup: BeautifulSoup, apar_number: str) -> str:
        """Extract all APAR information"""
        lines = []
        
        # Title - split APAR number and title
        title_text = soup.title.text
        lines.append(title_text[:7])  # APAR number
        if len(title_text) > 9:
            lines.append(title_text[9:])  # Title after "OA41368: "
        
        # Modified date
        doc_info = soup.find(id='ibm-document-information')
        if doc_info:
            date_p = doc_info.find('p')
            if date_p and len(date_p.contents) > 4:
                # Keep original formatting, remove first newline char
                date_text = date_p.contents[4][1:]
                lines.append(f"Document Modified Date: {date_text}")
        
        # Process sections
        for h2 in soup.find_all("h2"):
            section_name = h2.text
            
            if section_name in self.INFO_TYPES['type1']:
                lines.extend(self._parse_type1(h2))
            elif section_name in self.INFO_TYPES['type2']:
                lines.extend(self._parse_type2(h2, section_name))
            elif section_name in self.INFO_TYPES['type3']:
                lines.extend(self._parse_type3(h2, section_name))
            elif section_name in self.INFO_TYPES['type4']:
                lines.extend(self._parse_type4(h2, section_name))
        
        return '\n'.join(lines)
    
    def _extract_json(self, soup: BeautifulSoup, apar_number: str) -> dict:
        """Extract APAR information as JSON"""
        data = {'apar_number': apar_number}
        
        # Title
        title_text = soup.title.text
        data['title'] = title_text[9:] if len(title_text) > 9 else ''
        
        # Modified date
        doc_info = soup.find(id='ibm-document-information')
        if doc_info:
            date_p = doc_info.find('p')
            if date_p and len(date_p.contents) > 4:
                data['modified_date'] = date_p.contents[4].strip()
        
        # Process sections
        for h2 in soup.find_all("h2"):
            section_name = h2.text
            section_key = section_name.lower().replace(' ', '_')
            
            if section_name in self.INFO_TYPES['type1']:
                data[section_key] = self._parse_type1_json(h2)
            elif section_name in self.INFO_TYPES['type2']:
                data[section_key] = self._parse_type2_json(h2)
            elif section_name in self.INFO_TYPES['type3']:
                data[section_key] = self._parse_type3_json(h2)
            elif section_name in self.INFO_TYPES['type4']:
                data[section_key] = self._parse_type4_json(h2)
        
        return data
    
    def _parse_type1_json(self, h2) -> dict:
        """Parse APAR Information as JSON"""
        info = {}
        div = h2.find_next_sibling('div')
        if not div:
            return info
        
        ul = div.find('ul')
        if ul:
            for li in ul.find_all('li'):
                h3 = li.find('h3')
                p = li.find('p')
                if h3:
                    key = h3.text.lower().replace(' ', '_')
                    info[key] = p.text if p else ''
        
        ul = div.find_next_sibling('ul')
        if ul:
            routes = {'from': [], 'to': []}
            for li in ul.find_all('li'):
                h3 = li.find('h3')
                p = li.find('p')
                if h3 and 'FROM' in h3.text:
                    routes['from'] = p.text.strip().split() if p else []
                elif h3 and 'TO' in h3.text:
                    routes['to'] = p.text.strip().split() if p else []
            info['sysroute'] = routes
        
        return info
    
    def _parse_type2_json(self, h2) -> str:
        """Parse pre-formatted sections as JSON"""
        ul = h2.find_next_sibling('ul')
        if ul:
            li = ul.find('li')
            if li:
                pre = li.find('pre')
                if pre:
                    return pre.text
        return ''
    
    def _parse_type3_json(self, h2) -> list[dict]:
        """Parse tabular sections as JSON"""
        items = []
        ul = h2.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li'):
                parts = [child.text for child in li.children if hasattr(child, 'text')]
                if parts:
                    items.append({'fields': parts})
        return items
    
    def _parse_type4_json(self, h2) -> str:
        """Parse APAR status as JSON"""
        ul = h2.find_next_sibling('ul')
        if ul:
            h3 = ul.find('h3')
            if h3:
                return h3.text
        return ''

    def _parse_type1(self, h2) -> list[str]:
        """Parse APAR Information section"""
        lines = [h2.text]
        div = h2.find_next_sibling('div')
        if not div:
            return lines
        
        # First ul - basic info
        ul = div.find('ul')
        if ul:
            for li in ul.find_all('li'):
                h3 = li.find('h3')
                p = li.find('p')
                if h3:
                    lines.append(f"{h3.text}\t{p.text}" if p else h3.text)
        
        lines.append('')
        
        # Second ul - relationships
        ul = div.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li'):
                h3 = li.find('h3')
                p = li.find('p')
                if h3:
                    lines.append(f"{h3.text}\t{p.text[1:]}" if p else h3.text)
        
        lines.extend(['', '--', ''])
        return lines

    def _parse_type2(self, h2, section_name: str) -> list[str]:
        """Parse sections with pre-formatted text"""
        lines = [section_name]
        ul = h2.find_next_sibling('ul')
        if ul:
            li = ul.find('li')
            if li:
                pre = li.find('pre')
                if pre and pre.text.strip():
                    lines.append(pre.text.rstrip('\n'))
        lines.extend(['', '--', ''])
        return lines

    def _parse_type3(self, h2, section_name: str) -> list[str]:
        """Parse sections with tabular data"""
        lines = [section_name]
        ul = h2.find_next_sibling('ul')
        if ul:
            for li in ul.find_all('li'):
                parts = [child.text for child in li.children if hasattr(child, 'text')]
                lines.append('\t'.join(parts))
        lines.extend(['', ''])
        return lines

    def _parse_type4(self, h2, section_name: str) -> list[str]:
        """Parse APAR status section"""
        lines = [section_name]
        ul = h2.find_next_sibling('ul')
        if ul:
            h3 = ul.find('h3')
            if h3:
                lines.append(h3.text)
        lines.extend(['', ''])
        return lines

    def save_apar(self, apar_number: str, content: str | dict, status: str = 'success'):
        """Save APAR content to file"""
        suffix = '' if status == 'success' else f'.{status}'
        
        if self.output_format == 'json':
            output_file = self.output_dir / f"{apar_number}{suffix}.json"
            try:
                if isinstance(content, dict):
                    output_file.write_text(json.dumps(content, indent=2, ensure_ascii=False))
                else:
                    output_file.write_text(content, encoding='utf-8', errors='ignore')
                print(f"{apar_number} {'processing..' if status == 'success' else status}")
            except IOError as e:
                print(f"Error saving {apar_number}: {e}")
        else:
            output_file = self.output_dir / f"{apar_number}{suffix}.txt"
            try:
                if isinstance(content, str):
                    content = content.rstrip('\n') + '\n\n\n'
                output_file.write_text(content, encoding='utf-8', errors='ignore')
                print(f"{apar_number} {'processing..' if status == 'success' else status}")
            except IOError as e:
                print(f"Error saving {apar_number}: {e}")

    def process_apar(self, apar_number: str):
        """Process single APAR"""
        apar_number = apar_number.strip()[:7].upper()
        
        html = self.fetch_apar(apar_number)
        if not html:
            return
        
        status, content = self.parse_apar(apar_number, html)
        self.save_apar(apar_number, content, status)

    def process_file(self, input_file: Path):
        """Process APAR list from file"""
        try:
            with input_file.open('r') as f:
                for line in f:
                    if line.strip():
                        self.process_apar(line)
        except IOError as e:
            print(f"Error reading input file: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Parse IBM APAR (Authorized Program Analysis Report) information from IBM support pages.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  process a list of APARs from a file:
    apar-parser -i apar_list.txt -o output_dir

  process a single APAR:
    apar-parser -a OA41368 -o output_dir

  output in JSON format:
    apar-parser -i apar_list.txt -o output_dir -f json

  use GUI mode (Windows only):
    apar-parser --gui

input file format:
  plain text file with one APAR number per line:
    OA41368
    OA36415
    OA12345

output files:
  {APAR}.txt        - successfully parsed APAR (text format)
  {APAR}.json       - successfully parsed APAR (JSON format)
  {APAR}.notfound.txt - APAR not found
  {APAR}.logon.txt  - requires IBM ID login
"""
    )
    parser.add_argument('-i', '--input', type=Path,
                        help='input file containing APAR numbers (one per line)')
    parser.add_argument('-o', '--output', type=Path,
                        help='output directory where results will be saved (required unless using --gui)')
    parser.add_argument('-a', '--apar',
                        help='single APAR number to process (e.g. OA41368)')
    parser.add_argument('-f', '--format', choices=['txt', 'json'], default='txt',
                        help='output format: txt (default) or json for structured data')
    parser.add_argument('--gui', action='store_true',
                        help='use GUI dialogs for file/directory selection (Windows only, requires tkinter)')
    
    args = parser.parse_args()
    
    # GUI mode
    if args.gui:
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            
            output_dir = filedialog.askdirectory(title='Select output directory')
            if not output_dir:
                print('No output directory selected')
                sys.exit(1)
            
            input_file = filedialog.askopenfilename(title='Select APAR list file')
            if not input_file:
                print('No input file selected')
                sys.exit(1)
            
            args.output = Path(output_dir)
            args.input = Path(input_file)
        except ImportError:
            print('tkinter not available')
            sys.exit(1)
    
    # Validate arguments
    if not args.output:
        parser.error('--output is required (or use --gui)')
    if not args.apar and not args.input:
        parser.error('Either --input or --apar must be specified')
    
    # Process
    apar_parser = APARParser(args.output, args.format)
    
    if args.apar:
        apar_parser.process_apar(args.apar)
    else:
        apar_parser.process_file(args.input)


if __name__ == '__main__':
    main()
