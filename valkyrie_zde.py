#!/usr/bin/env python3
"""
VALKYRIE ZERO-DAY ENGINE v4.0
Advanced Heuristic Anomaly Detection Framework

Copyright (c) 2024 F1REW0LF
License: MIT - For authorized security testing only

Tactical Objectives:
1. Zero-Day Vulnerability Discovery
2. Heuristic Behavioral Analysis
3. WAF/SIEM Evasion
4. Automated Reconnaissance
"""

import requests
import urllib3
import sys
import time
import json
import os
import threading
import queue
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from datetime import datetime
from collections import defaultdict
import hashlib
import base64
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== VERSION & INFO ====================
VERSION = "4.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT - Open Source"

# ==================== COLOR CODES ====================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

def cprint(text, color=Colors.WHITE, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.WHITE}")
    else:
        print(f"{color}{text}{Colors.WHITE}")

# ==================== MUTATION GENERATOR ====================
class MutationGenerator:
    """Generate diverse mutation vectors for heuristic fuzzing"""
    
    @staticmethod
    def generate_mutations():
        """Generate comprehensive mutation vectors"""
        
        mutations = {
            # 1. Array/List Injections
            "array_basic": {"id[]": "test"},
            "array_multi": {"id[]": ["test1", "test2", "test3"]},
            "array_nested": {"id[0][key]": "value"},
            "array_overflow": {"id[]": ["A" * 10000]},
            
            # 2. Null Byte Injections
            "null_byte": {"id": "%00"},
            "null_byte_mid": {"id": "test%00payload"},
            "null_byte_encoded": {"id": "%2500"},
            "null_byte_hex": {"id": "\\x00"},
            
            # 3. Type Confusion
            "type_boolean": {"id": "true"},
            "type_null": {"id": "null"},
            "type_undefined": {"id": "undefined"},
            "type_numeric": {"id": "1e309"},
            "type_infinity": {"id": "Infinity"},
            "type_nan": {"id": "NaN"},
            
            # 4. Unicode/Overflow
            "unicode_basic": {"id": "𝔡𝔢𝔞𝔡𝔟𝔢𝔢𝔣"},
            "unicode_overflow": {"id": "A" * 5000 + "𝔡𝔢𝔞𝔡𝔟𝔢𝔢𝔣"},
            "unicode_emoji": {"id": "😂😊😍🔥💀"},
            "unicode_rtl": {"id": "سلام"},
            "unicode_zero_width": {"id": "test" + u'\u200b' * 100},
            
            # 5. SQL-like Injections (Without Signatures)
            "sql_comparison": {"id": "' OR '1'='1'"},
            "sql_union": {"id": "' UNION SELECT NULL--"},
            "sql_sleep": {"id": "' AND SLEEP(5)--"},
            "sql_comment": {"id": "' OR 1=1#"},
            
            # 6. Path Traversal (Without Signatures)
            "path_dotdot": {"file": "../../../etc/passwd"},
            "path_encoded": {"file": "%2e%2e%2f%2e%2e%2f"},
            "path_windows": {"file": "..\\..\\..\\windows\\win.ini"},
            "path_absolute": {"file": "/etc/passwd"},
            
            # 7. Buffer Overflow Patterns
            "buffer_long": {"id": "A" * 5000},
            "buffer_repeat": {"id": "%x" * 100},
            "buffer_format": {"id": "%p" * 50 + "%n" * 10},
            
            # 8. HTTP Parameter Pollution
            "hpp_basic": {"id": ["value1", "value2"]},
            "hpp_duplicate": {"id": "test", "id": "test2"},
            "hpp_case": {"ID": "test", "id": "test2"},
            
            # 9. XML/JSON Injection
            "xml_tag": {"id": "<test>value</test>"},
            "xml_comment": {"id": "<!-- comment -->"},
            "json_inject": {"id": '{"key":"value"}'},
            
            # 10. Special Characters
            "special_chars": {"id": "!@#$%^&*()_+-=[]{}|;:'\",.<>?/"},
            "special_control": {"id": "\x00\x01\x02\x03"},
            "special_escape": {"id": "\\n\\r\\t\\b"},
            
            # 11. Long Parameter Names
            "long_param": {"A" * 1000: "value"},
            "long_param_unicode": {"参数" * 100: "value"},
            
            # 12. Multi-part Form Data
            "multipart_boundary": {"id": "test", "boundary": "---"},
            "multipart_extra": {"id": "test", "extra": "data"},
            
            # 13. Cookie Manipulation
            "cookie_inject": {"id": "test", "Cookie": "sessionid=malicious"},
            
            # 14. Content-Type Manipulation
            "content_type": {"id": "test", "Content-Type": "application/xml"},
            
            # 15. Method Override
            "method_override": {"id": "test", "_method": "PUT"}
        }
        
        return mutations

# ==================== PATH DISCOVERY ====================
class PathDiscovery:
    """Automated path discovery from various sources"""
    
    COMMON_PATHS = [
        "/admin", "/api", "/config", "/console", "/debug",
        "/docs", "/log", "/logs", "/manage", "/portal",
        "/private", "/prod", "/secret", "/secure", "/status",
        "/test", "/tmp", "/trace", "/web", "/ws",
        "/.git", "/.env", "/.aws", "/.ssh", "/.config"
    ]
    
    @staticmethod
    def discover_from_robots(target_url):
        """Extract paths from robots.txt"""
        paths = []
        try:
            robots_url = urljoin(target_url, "/robots.txt")
            response = requests.get(robots_url, timeout=5, verify=False)
            
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line.lower().startswith(('disallow:', 'allow:')):
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/':
                            paths.append(path)
                cprint(f"[+] Found {len(paths)} paths in robots.txt", Colors.GREEN)
        except:
            pass
        return paths
    
    @staticmethod
    def discover_from_sitemap(target_url):
        """Extract paths from sitemap.xml"""
        paths = []
        try:
            sitemap_url = urljoin(target_url, "/sitemap.xml")
            response = requests.get(sitemap_url, timeout=5, verify=False)
            
            if response.status_code == 200:
                import re
                urls = re.findall(r'<loc>(.*?)</loc>', response.text)
                for url in urls:
                    parsed = urlparse(url)
                    if parsed.path and parsed.path != '/':
                        paths.append(parsed.path)
                cprint(f"[+] Found {len(paths)} paths in sitemap.xml", Colors.GREEN)
        except:
            pass
        return paths
    
    @staticmethod
    def discover_common_paths():
        """Return common admin/private paths"""
        return PathDiscovery.COMMON_PATHS
    
    @staticmethod
    def discover_all(target_url):
        """Discover paths from all sources"""
        all_paths = set()
        
        # From robots.txt
        all_paths.update(PathDiscovery.discover_from_robots(target_url))
        
        # From sitemap.xml
        all_paths.update(PathDiscovery.discover_from_sitemap(target_url))
        
        # Common paths
        all_paths.update(PathDiscovery.discover_common_paths())
        
        return list(all_paths)

# ==================== ANOMALY DETECTOR ====================
class AnomalyDetector:
    """Detect anomalies in HTTP responses"""
    
    def __init__(self, baseline_response, baseline_time, baseline_size):
        self.baseline = {
            'response': baseline_response,
            'time': baseline_time,
            'size': baseline_size,
            'status': baseline_response.status_code
        }
        self.anomalies = []
        
    def analyze(self, response, response_time, mutation_name, test_url):
        """Analyze response for anomalies"""
        anomalies = []
        
        # 1. Check status code
        if response.status_code == 500:
            anomalies.append({
                'type': 'unhandled_exception',
                'severity': 'critical',
                'description': 'HTTP 500 Internal Error - Unhandled exception',
                'details': f'Status Code: {response.status_code}'
            })
        
        # 2. Check for error responses
        error_indicators = ['error', 'exception', 'stack trace', 'warning', 'fatal']
        response_text = response.text.lower()
        if any(indicator in response_text for indicator in error_indicators):
            anomalies.append({
                'type': 'error_disclosure',
                'severity': 'high',
                'description': 'Error information disclosed in response',
                'details': f'Contains error indicators in response body'
            })
        
        # 3. Check time deviation
        time_diff = abs(response_time - self.baseline['time'])
        if time_diff > 3.0:
            anomalies.append({
                'type': 'time_anomaly',
                'severity': 'medium',
                'description': f'Significant time deviation: {response_time:.2f}s (baseline: {self.baseline["time"]:.2f}s)',
                'details': f'Time difference: {time_diff:.2f}s'
            })
        
        # 4. Check size deviation
        response_size = len(response.text)
        size_diff = abs(response_size - self.baseline['size'])
        size_percent = (size_diff / self.baseline['size']) * 100 if self.baseline['size'] > 0 else 0
        
        if size_percent > 50:
            anomalies.append({
                'type': 'size_anomaly',
                'severity': 'medium',
                'description': f'Significant size deviation: {size_percent:.1f}%',
                'details': f'Size: {response_size} bytes (baseline: {self.baseline["size"]} bytes)'
            })
        
        # 5. Check for stack trace patterns
        stack_patterns = ['File "', 'line ', 'Traceback', 'at ', '.java:', '.php:']
        if any(pattern in response.text for pattern in stack_patterns):
            anomalies.append({
                'type': 'stack_trace_leak',
                'severity': 'critical',
                'description': 'Stack trace information leaked',
                'details': 'Server stack trace detected in response'
            })
        
        return anomalies

# ==================== MAIN ENGINE ====================
class ValkyrieZeroDayEngine:
    """Advanced Heuristic Anomaly Detection Framework"""
    
    def __init__(self, target_url, verbose=False):
        self.target_url = target_url
        self.verbose = verbose
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close'
        })
        self.mutation_gen = MutationGenerator()
        self.path_discovery = PathDiscovery()
        self.anomalies = []
        self.scanned_urls = []
        self.start_time = time.time()
        
        # Statistics
        self.stats = {
            'total_mutations': 0,
            'critical_anomalies': 0,
            'high_anomalies': 0,
            'medium_anomalies': 0,
            'paths_discovered': 0,
            'scan_time': 0
        }
        
        # Threading
        self.queue = queue.Queue()
        self.results = []
        self.lock = threading.Lock()
        
    def banner(self):
        """Display banner"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        banner = f"""
{Colors.PURPLE}{Colors.BOLD}    ██╗   ██╗ █████╗ ██╗     ██╗  ██╗██╗██████╗ ██╗███████╗
    ██║   ██║██╔══██╗██║     ██║ ██╔╝██║██╔══██╗██║██╔════╝
    ██║   ██║███████║██║     █████╔╝ ██║██████╔╝██║█████╗  
    ╚██╗ ██╔╝██╔══██║██║     ██╔═██╗ ██║██╔══██╗██║██╔══╝  
     ╚████╔╝ ██║  ██║███████╗██║  ██╗██║██║  ██║██║███████╗
      ╚═══╝  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝╚══════╝
                                                                                                   
{Colors.GREEN}                    ZERO-DAY ENGINE v{VERSION}{Colors.WHITE}
{Colors.YELLOW}          Heuristic Anomaly Detection Framework{Colors.WHITE}
{Colors.CYAN}    Tactical: Zero-Signature Fuzzing | Behavioral Analysis | Path Discovery{Colors.WHITE}
        """
        print(banner)
        cprint(f"[*] Target: {self.target_url}", Colors.CYAN)
        cprint(f"[*] Scan Mode: Heuristic Anomaly Detection", Colors.CYAN)
        print("-" * 80)
    
    def establish_baseline(self):
        """Establish baseline response profile"""
        cprint("\n[*] Establishing baseline profile...", Colors.YELLOW)
        
        try:
            start_time = time.time()
            response = self.session.get(self.target_url, timeout=10)
            response_time = time.time() - start_time
            response_size = len(response.text)
            
            cprint(f"[+] Baseline established:", Colors.GREEN)
            cprint(f"    Status: {response.status_code}", Colors.DIM)
            cprint(f"    Time: {response_time:.3f}s", Colors.DIM)
            cprint(f"    Size: {response_size} bytes", Colors.DIM)
            cprint(f"    Headers: {len(response.headers)} headers", Colors.DIM)
            
            return response, response_time, response_size
            
        except Exception as e:
            cprint(f"[-] Failed to establish baseline: {e}", Colors.RED)
            return None, 0, 0
    
    def discover_paths(self):
        """Discover hidden paths"""
        cprint("\n[*] Discovering hidden paths...", Colors.YELLOW)
        
        paths = self.path_discovery.discover_all(self.target_url)
        
        if paths:
            cprint(f"[+] Discovered {len(paths)} paths:", Colors.GREEN)
            for path in paths[:10]:
                cprint(f"    {path}", Colors.DIM)
            if len(paths) > 10:
                cprint(f"    ... and {len(paths) - 10} more", Colors.DIM)
            self.stats['paths_discovered'] = len(paths)
        else:
            cprint("[!] No hidden paths discovered", Colors.YELLOW)
        
        return paths
    
    def scan_mutation(self, mutation_name, payload, base_url, detector):
        """Scan a single mutation"""
        try:
            # Build URL with query parameters
            parsed_url = urlparse(base_url)
            base_endpoint = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            test_url = f"{base_endpoint}?{urlencode(payload)}"
            
            # Add to scanned urls
            self.scanned_urls.append(test_url)
            
            # Send request
            start_time = time.time()
            response = self.session.get(test_url, timeout=10)
            response_time = time.time() - start_time
            
            # Analyze for anomalies
            anomalies = detector.analyze(
                response, 
                response_time, 
                mutation_name, 
                test_url
            )
            
            # Process anomalies
            if anomalies:
                with self.lock:
                    self.anomalies.extend(anomalies)
                    self.results.append({
                        'mutation': mutation_name,
                        'url': test_url,
                        'anomalies': anomalies,
                        'status': response.status_code,
                        'time': response_time,
                        'size': len(response.text)
                    })
                
                for anomaly in anomalies:
                    if anomaly['severity'] == 'critical':
                        self.stats['critical_anomalies'] += 1
                    elif anomaly['severity'] == 'high':
                        self.stats['high_anomalies'] += 1
                    else:
                        self.stats['medium_anomalies'] += 1
                    
                    if self.verbose:
                        cprint(f"\n[!] {anomaly['type'].upper()}: {anomaly['description']}", 
                               Colors.RED if anomaly['severity'] == 'critical' else Colors.YELLOW)
                        cprint(f"    URL: {test_url}", Colors.DIM)
                        cprint(f"    {anomaly['details']}", Colors.DIM)
            
            self.stats['total_mutations'] += 1
            
            # Progress indicator
            if self.stats['total_mutations'] % 10 == 0:
                sys.stdout.write(f"\r[*] Progress: {self.stats['total_mutations']} mutations scanned")
                sys.stdout.flush()
                
        except requests.exceptions.Timeout:
            with self.lock:
                self.results.append({
                    'mutation': mutation_name,
                    'url': test_url,
                    'error': 'Timeout',
                    'status': 'TIMEOUT'
                })
            cprint(f"\n[-] Timeout: {test_url}", Colors.RED)
        except Exception as e:
            if self.verbose:
                cprint(f"\n[-] Error scanning {mutation_name}: {e}", Colors.RED)
    
    def scan_worker(self, detector, base_url):
        """Worker thread for scanning"""
        while True:
            try:
                mutation_name, payload = self.queue.get(timeout=1)
                self.scan_mutation(mutation_name, payload, base_url, detector)
                self.queue.task_done()
            except:
                break
    
    def scan_mutations(self, detector, base_url, mutations):
        """Scan all mutations using multiple threads"""
        cprint("\n[*] Scanning mutations...", Colors.YELLOW)
        
        # Add mutations to queue
        for name, payload in mutations.items():
            self.queue.put((name, payload))
        
        # Start worker threads
        threads = []
        num_threads = min(10, len(mutations))
        
        for _ in range(num_threads):
            t = threading.Thread(target=self.scan_worker, args=(detector, base_url))
            t.daemon = True
            t.start()
            threads.append(t)
        
        # Wait for completion
        self.queue.join()
        
        cprint(f"\n[+] Scan complete: {self.stats['total_mutations']} mutations analyzed", Colors.GREEN)
    
    def generate_report(self):
        """Generate comprehensive report"""
        cprint("\n" + "="*80)
        cprint(" SCAN REPORT", Colors.BOLD, bold=True)
        cprint("="*80)
        
        # Summary
        cprint("\n[+] SCAN SUMMARY:", Colors.CYAN)
        cprint(f"    Target: {self.target_url}", Colors.WHITE)
        cprint(f"    Total Mutations: {self.stats['total_mutations']}", Colors.WHITE)
        cprint(f"    Paths Discovered: {self.stats['paths_discovered']}", Colors.WHITE)
        cprint(f"    Scan Duration: {time.time() - self.start_time:.2f}s", Colors.WHITE)
        
        # Anomaly Statistics
        cprint("\n[+] ANOMALY STATISTICS:", Colors.CYAN)
        cprint(f"    Critical: {Colors.RED}{self.stats['critical_anomalies']}{Colors.WHITE}")
        cprint(f"    High: {Colors.YELLOW}{self.stats['high_anomalies']}{Colors.WHITE}")
        cprint(f"    Medium: {Colors.BLUE}{self.stats['medium_anomalies']}{Colors.WHITE}")
        
        # Detailed Anomalies
        if self.anomalies:
            cprint("\n[+] DETAILED ANOMALIES:", Colors.CYAN)
            for i, anomaly in enumerate(self.anomalies[:20], 1):
                color = Colors.RED if anomaly['severity'] == 'critical' else Colors.YELLOW
                cprint(f"\n    {i}. [{anomaly['severity'].upper()}] {anomaly['type']}", color)
                cprint(f"       {anomaly['description']}", Colors.DIM)
                cprint(f"       {anomaly['details']}", Colors.DIM)
            
            if len(self.anomalies) > 20:
                cprint(f"\n    ... and {len(self.anomalies) - 20} more anomalies", Colors.DIM)
        else:
            cprint("\n[+] No anomalies detected", Colors.GREEN)
        
        # Recommendations
        cprint("\n[+] RECOMMENDATIONS:", Colors.CYAN)
        if self.stats['critical_anomalies'] > 0:
            cprint("    - IMMEDIATE: Investigate critical anomalies for potential zero-days", Colors.RED)
        if self.stats['high_anomalies'] > 0:
            cprint("    - HIGH: Review high-severity anomalies for security implications", Colors.YELLOW)
        if self.stats['paths_discovered'] > 0:
            cprint("    - INFO: Review discovered paths for sensitive information exposure", Colors.BLUE)
        
        # Save report
        self.save_report()
        
        print("="*80 + "\n")
    
    def save_report(self):
        """Save scan results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"valkyrie_report_{timestamp}.json"
        
        report_data = {
            'target': self.target_url,
            'timestamp': datetime.now().isoformat(),
            'duration': time.time() - self.start_time,
            'statistics': self.stats,
            'anomalies': self.anomalies,
            'results': self.results,
            'scanned_urls': self.scanned_urls[:100]  # Limit
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        cprint(f"\n[+] Report saved to: {filename}", Colors.GREEN)
    
    def run(self):
        """Execute the scan"""
        self.banner()
        
        # Establish baseline
        baseline_response, baseline_time, baseline_size = self.establish_baseline()
        if not baseline_response:
            cprint("[-] Scan aborted: Could not establish baseline", Colors.RED)
            return
        
        # Initialize detector
        detector = AnomalyDetector(baseline_response, baseline_time, baseline_size)
        
        # Discover hidden paths
        paths = self.discover_paths()
        
        # Generate mutations
        mutations = self.mutation_gen.generate_mutations()
        
        # Parse base URL
        parsed_url = urlparse(self.target_url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        
        # Scan mutations on main URL
        self.scan_mutations(detector, base_url, mutations)
        
        # Scan discovered paths
        if paths:
            cprint(f"\n[*] Scanning discovered paths...", Colors.YELLOW)
            for path in paths:
                if path.startswith('/'):
                    path_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"
                else:
                    path_url = urljoin(base_url, path)
                
                # Skip if already scanned
                if path_url in self.scanned_urls:
                    continue
                
                cprint(f"[*] Scanning: {path_url}", Colors.DIM)
                self.scan_mutations(detector, path_url, mutations)
        
        # Generate report
        self.generate_report()

# ==================== MAIN ====================
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════════════════╗
    ║  WARNING: Advanced Zero-Day Discovery Tool                         ║
    ║  For authorized security testing only.                            ║
    ║  Users are responsible for legal compliance.                      ║
    ╚═══════════════════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        cprint("[*] Usage: python3 valkyrie_zde_v4.py <URL> [--verbose]", Colors.YELLOW)
        cprint("[*] Example: python3 valkyrie_zde_v4.py https://target.com", Colors.YELLOW)
        cprint("[*] Example: python3 valkyrie_zde_v4.py https://target.com --verbose", Colors.YELLOW)
        sys.exit(1)
    
    target = sys.argv[1]
    verbose = "--verbose" in sys.argv
    
    engine = ValkyrieZeroDayEngine(target, verbose)
    
    try:
        engine.run()
    except KeyboardInterrupt:
        cprint("\n\n[!] Scan interrupted by user", Colors.RED)
        sys.exit(0)
