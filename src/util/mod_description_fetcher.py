'''Enhanced Mod Description Fetcher with Category Support - UPDATED'''
# pylint: disable=invalid-name,missing-docstring

import os
import re
import time
import json
import sqlite3
import random
import urllib.robotparser
import yaml
from typing import Optional, List, Dict, Tuple
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.globals import data
from src.util.util import normalizePath, getProgramRootFolder
from src.util.text_sanitize import sanitize_text_for_ui

class CategoryManager:
    '''Manager for handling category mapping'''
    
    def __init__(self):
        self.category_map = {}
        self.load_category_mapping()
    
    def load_category_mapping(self):
        '''Load category mapping from YAML or JSON file'''
        # Try loading from YAML file first
        yaml_path = normalizePath(getProgramRootFolder() + "/mapping/category_mapping.yaml")
        json_path = normalizePath(getProgramRootFolder() + "/api/get_category/witcher3_categories.json")
        
        try:
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    self.category_map = data.get('Category_Mapping', {})
                    print(f"Loaded category mapping from YAML: {len(self.category_map)} categories")
            elif os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    self.category_map = json.load(f)
                    print(f"Loaded category mapping from JSON: {len(self.category_map)} categories")
            else:
                print("No category mapping file found, using fallback mapping")
                self.category_map = self._get_fallback_mapping()
        except Exception as e:
            print(f"Error loading category mapping: {e}")
            self.category_map = self._get_fallback_mapping()
    
    def _get_fallback_mapping(self) -> Dict[str, str]:
        '''Fallback category mapping if file loading fails'''
        return {
            "1": "The Witcher 3",
            "2": "Miscellaneous", 
            "3": "Controller Button Layout",
            "4": "Visuals and Graphics",
            "5": "Skills and Leveling",
            "6": "User Interface",
            "8": "Tweaks",
            "10": "Armour",
            "11": "Cheats and God items",
            "12": "Bug Fixes",
            "13": "Combat",
            "14": "Gwent",
            "15": "Modders Resources and Tutorials",
            "16": "ReShade Preset",
            "17": "Gameplay Changes",
            "18": "Models and Textures",
            "19": "Weapons",
            "20": "Signs",
            "21": "Save Games",
            "22": "Overhaul",
            "23": "Characters",
            "24": "Items",
            "25": "Camera",
            "27": "Debug Console",
            "28": "Alchemy and Crafting",
            "29": "Weapons and Armour",
            "30": "Inventory",
            "31": "Balancing",
            "32": "Immersion",
            "33": "Utilities",
            "35": "Audio",
            "40": "Performance",
            "41": "Hair and Face",
            "42": "Quests and Adventures"
        }
    
    def get_category_name(self, category_id: str) -> str:
        '''Get category name from ID'''
        return self.category_map.get(str(category_id), "Miscellaneous")
    
    def normalize_category_name(self, category_name: str) -> str:
        '''Normalize category name from web scraping'''
        if not category_name:
            return "Miscellaneous"
        
        # Clean up category name
        category_name = category_name.strip()
        
        # Map some common names
        mapping = {
            "Models and Textures": "Models and Textures",
            "Weapons and Armour": "Weapons and Armour", 
            "Alchemy and Crafting": "Alchemy and Crafting",
            "Visuals and Graphics": "Visuals and Graphics",
            "Skills and Leveling": "Skills and Leveling",
            "Controller Button Layout": "Controller Button Layout",
            "Modders Resources and Tutorials": "Modders Resources and Tutorials"
        }
        
        return mapping.get(category_name, category_name)


class NexusAPI:
    '''Nexus Mods API wrapper'''
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.nexusmods.com/v1"
        self.game_domain = "witcher3"
        self.session = self._setup_session()
        self.category_manager = CategoryManager()
    
    def _setup_session(self) -> requests.Session:
        '''Setup session for API requests'''
        session = requests.Session()
        
        if self.api_key:
            session.headers.update({
                'apikey': self.api_key,
                'User-Agent': 'TW3-Mod-Manager/0.9.3',
                'Application-Name': 'TW3-Mod-Manager',
                'Application-Version': '0.9.3',
                'Content-Type': 'application/json'
            })
        
        # Retry strategy
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def get_mod_info(self, mod_id: str) -> Optional[dict]:
        '''Get mod info from Nexus API'''
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/games/{self.game_domain}/mods/{mod_id}.json"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 401:
                raise Exception("API key is invalid or expired")
            elif response.status_code == 403:
                raise Exception("No permission to access API")
            elif response.status_code == 404:
                return None  # Mod does not exist
            elif response.status_code == 429:
                raise Exception("API rate limit exceeded")
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            raise Exception(f"API connection error: {str(e)}")
    
    def extract_description_from_api_data(self, api_data: dict) -> str:
        '''Extract description from API data'''
        if not api_data:
            return "Mod information not found"
        
        # Priority: description -> summary -> name
        description = ""
        
        # Check description field first
        if 'description' in api_data and api_data['description']:
            raw_desc = api_data['description']
            # Remove BBCode and HTML tags
            description = self._clean_description(raw_desc)
        
        # If description is empty or too short, use summary
        if not description or len(description.strip()) < 20:
            if 'summary' in api_data and api_data['summary']:
                description = api_data['summary']
        
        # If still not available, use name
        if not description or len(description.strip()) < 10:
            if 'name' in api_data and api_data['name']:
                description = f"Mod: {api_data['name']}"
        
        return description or "No description from API"
    
    def extract_category_from_api_data(self, api_data: dict) -> str:
        '''Extract category from API data'''
        if not api_data:
            return "Miscellaneous"
        
        category_id = api_data.get('category_id')
        if category_id:
            return self.category_manager.get_category_name(str(category_id))
        
        return "Miscellaneous"
    
    def _clean_description(self, raw_text: str) -> str:
        '''Clean description from BBCode and HTML'''
        if not raw_text:
            return ""
        
        # Remove BBCode tags
        text = re.sub(r'\[/?[^\]]+\]', '', raw_text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'https?://[^\s]+', '', text)
        
        # Remove multiple whitespaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Get the first meaningful paragraph (usually the main description)
        lines = text.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Only take lines with significant content
                meaningful_lines.append(line)
                if len(' '.join(meaningful_lines)) > 200:  # Limit length
                    break
        
        result = ' '.join(meaningful_lines).strip()
        
        # If result is too long, cut at the nearest complete sentence
        if len(result) > 500:
            sentences = re.split(r'[.!?]\s+', result)
            result = ""
            for sentence in sentences:
                if len(result + sentence) > 400:
                    break
                result += sentence + ". "
            result = result.strip()
        
        return result or raw_text[:200] + "..." if len(raw_text) > 200 else raw_text


class SafeWebScraper:
    '''Enhanced safe web scraper with full protection features'''
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.domain = "nexusmods.com"
        self.category_manager = CategoryManager()
        
        # Global rate limiting - HARD LIMIT: 20 requests/minute
        self.global_rate_limit = 20  # requests per minute
        self.global_requests = []  # [(timestamp, request_info), ...]
        
        # Exponential backoff settings
        self.base_delay = 3.0  # base delay in seconds
        self.max_delay = 60.0  # max delay in seconds
        self.backoff_multiplier = 2
        
        # Request tracking
        self._consecutive_errors = 0
        self._last_successful_request = time.time()
        
        # Robots.txt settings
        self.crawl_delay = None
        self.robots_parser = None
        self._check_robots_txt()
        
        # Session setup
        self.session = self._create_safe_session()
        
        # User-agent rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'The Witcher 3 Mod Manager - Community Tool v0.9.3 (Contact: support@example.com)'
        ]
    
    def _check_robots_txt(self):
        '''Check and comply with robots.txt'''
        try:
            robots_url = f"https://{self.domain}/robots.txt"
            self.robots_parser = urllib.robotparser.RobotFileParser()
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            
            # Get crawl-delay if available
            crawl_delay = self.robots_parser.crawl_delay("*")
            if crawl_delay:
                self.crawl_delay = float(crawl_delay)
                print(f"Robots.txt crawl-delay: {self.crawl_delay}s")
            else:
                self.crawl_delay = 3.0  # Default safe delay
                
        except Exception as e:
            print(f"Warning: Could not read robots.txt: {e}")
            self.crawl_delay = 5.0  # Conservative default
    
    def _create_safe_session(self) -> requests.Session:
        '''Create a safe session with full headers'''
        session = requests.Session()
        
        # Conservative retry strategy
        retry_strategy = Retry(
            total=2,  # Reduce retries to avoid spamming
            backoff_factor=2,
            status_forcelist=[500, 502, 503, 504],  # Do not retry 429 - handle separately
            allowed_methods=["GET"],
            raise_on_status=False  # To handle status codes manually
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _update_session_headers(self):
        '''Update headers for session with realistic info'''
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Referer': f'https://{self.domain}/witcher3',  # Valid referer
            'DNT': '1',  # Do Not Track
            'Cache-Control': 'no-cache',
        })
    
    def _check_global_rate_limit(self):
        '''Check and enforce global rate limit'''
        current_time = time.time()
        
        # Remove requests older than 1 minute
        self.global_requests = [
            (timestamp, info) for timestamp, info in self.global_requests 
            if current_time - timestamp < 60
        ]
        
        # Check if limit exceeded
        if len(self.global_requests) >= self.global_rate_limit:
            oldest_request = min(self.global_requests, key=lambda x: x[0])
            wait_time = 60 - (current_time - oldest_request[0])
            
            if wait_time > 0:
                print(f"Global rate limit reached. Waiting {wait_time:.2f}s")
                time.sleep(wait_time)
    
    def _calculate_delay(self, retry_count: int = 0) -> float:
        '''Calculate delay with exponential backoff + jitter'''
        if self._consecutive_errors > 0:
            # Exponential backoff for consecutive errors
            backoff = self.base_delay * (self.backoff_multiplier ** self._consecutive_errors)
            backoff = min(backoff, self.max_delay)
        else:
            # Normal delay based on robots.txt or default
            backoff = self.crawl_delay or self.base_delay
        
        # Add random jitter (±20%)
        jitter = random.uniform(-0.2, 0.2) * backoff
        final_delay = max(1.0, backoff + jitter)
        
        return final_delay
    
    def _handle_429_response(self, response: requests.Response) -> float:
        '''Handle 429 response with Retry-After header'''
        retry_after = response.headers.get('Retry-After')
        
        if retry_after:
            try:
                # Retry-After can be seconds or HTTP date
                if retry_after.isdigit():
                    delay = int(retry_after)
                else:
                    # Parse HTTP date format
                    from datetime import datetime
                    retry_time = datetime.strptime(retry_after, '%a, %d %b %Y %H:%M:%S GMT')
                    delay = (retry_time - datetime.utcnow()).total_seconds()
                
                delay = max(1, min(delay, 300))  # Cap at 5 minutes
                print(f"Rate limited (429). Retry-After: {delay}s")
                return delay
                
            except (ValueError, TypeError):
                pass
        
        # Fallback if no Retry-After or parse error
        delay = self._calculate_delay(retry_count=self._consecutive_errors + 1)
        print(f"Rate limited (429). Using backoff delay: {delay:.2f}s")
        return delay
    
    def _respect_delays(self):
        '''Enforce all necessary delays'''
        # Check global rate limit
        self._check_global_rate_limit()
        
        # Calculate and apply delay
        delay = self._calculate_delay()
        
        print(f"Applying delay: {delay:.2f}s (errors: {self._consecutive_errors})")
        time.sleep(delay)
    
    def _can_fetch(self, url: str) -> bool:
        '''Check if allowed to fetch this URL'''
        if self.robots_parser:
            user_agent = self.session.headers.get('User-Agent', '*')
            return self.robots_parser.can_fetch(user_agent, url)
        return True
    
    def fetch_page(self, mod_id: str, max_retries: int = 2) -> Optional[str]:
        '''Fetch web page with full safety measures'''
        url = f"{self.base_url}{mod_id}"
        
        # Check robots.txt
        if not self._can_fetch(url):
            print(f"Robots.txt disallows fetching {url}")
            return None
        
        for attempt in range(max_retries + 1):
            try:
                # Update headers for each request
                self._update_session_headers()
                
                # Apply delays
                self._respect_delays()
                
                print(f"Fetching {url} (attempt {attempt + 1}/{max_retries + 1})")
                
                # Track request
                current_time = time.time()
                self.global_requests.append((current_time, {'url': url, 'attempt': attempt + 1}))
                
                # Make request
                response = self.session.get(url, timeout=15, allow_redirects=True)
                
                # Handle response codes
                if response.status_code == 200:
                    self._consecutive_errors = 0
                    self._last_successful_request = current_time
                    print(f"✓ Successfully fetched {url}")
                    return response.text
                    
                elif response.status_code == 404:
                    print(f"Mod {mod_id} not found (404)")
                    return None
                    
                elif response.status_code == 429:
                    delay = self._handle_429_response(response)
                    if attempt < max_retries:
                        time.sleep(delay)
                        continue
                    else:
                        print(f"Rate limited after {max_retries + 1} attempts")
                        return None
                        
                elif response.status_code == 403:
                    print(f"Access forbidden (403) for {url}")
                    self._consecutive_errors += 1
                    return None
                    
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    self._consecutive_errors += 1
                    if attempt < max_retries:
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                print(f"Timeout for {url} (attempt {attempt + 1})")
                self._consecutive_errors += 1
                if attempt < max_retries:
                    time.sleep(self._calculate_delay(attempt))
                    continue
                return None
                
            except requests.exceptions.ConnectionError as e:
                print(f"Connection error for {url}: {e}")
                self._consecutive_errors += 1
                if attempt < max_retries:
                    time.sleep(self._calculate_delay(attempt))
                    continue
                return None
                
            except Exception as e:
                print(f"Unexpected error for {url}: {e}")
                self._consecutive_errors += 1
                if attempt < max_retries:
                    time.sleep(self._calculate_delay(attempt))
                    continue
                return None
        
        return None
    
    def get_health_status(self) -> dict:
        '''Get information about scraper health'''
        current_time = time.time()
        recent_requests = [
            req for req in self.global_requests 
            if current_time - req[0] < 300  # Last 5 minutes
        ]
        
        return {
            'consecutive_errors': self._consecutive_errors,
            'requests_last_5min': len(recent_requests),
            'global_rate_limit': self.global_rate_limit,
            'current_crawl_delay': self.crawl_delay,
            'time_since_last_success': current_time - self._last_successful_request,
            'status': 'healthy' if self._consecutive_errors < 3 else 'degraded'
        }


class ModDescriptionFetcher:
    '''Enhanced Fetcher with Nexus API integration and safe web scraping'''
    
    def __init__(self):
        self.db_path = normalizePath(data.config.configuration + '/mod_descriptions.db')
        self.base_url = "https://www.nexusmods.com/witcher3/mods/"
        
        # Initialize safe web scraper
        self.web_scraper = SafeWebScraper(self.base_url)
        
        # Initialize Nexus API
        self.nexus_api = None
        self.api_status = "not_checked"  # not_checked, available, unavailable, invalid
        self._check_and_setup_api()
        
        # Initialize database
        self.init_database()
    
    def _check_and_setup_api(self):
        '''Check and setup Nexus API'''
        api_key = self._get_api_key()
        
        if api_key:
            self.nexus_api = NexusAPI(api_key)
            self.api_status = "available"
            print("Nexus API configured successfully")
        else:
            self.nexus_api = None
            self.api_status = "unavailable"
            print("Nexus API not configured, will use safe web scraping")
    
    def _get_api_key(self) -> Optional[str]:
        '''Get API key from environment variable or file'''
        # Try environment variable first
        api_key = os.environ.get("NEXUS_API_KEY")
        if api_key and api_key.strip():
            return api_key.strip()
        
        # Try file api_key.txt in api folder
        try:
            api_folder = normalizePath(getProgramRootFolder() + "/api")
            api_key_file = normalizePath(api_folder + "/api_key.txt")
            
            if os.path.exists(api_key_file):
                with open(api_key_file, 'r', encoding='utf-8') as f:
                    api_key = f.read().strip()
                    if api_key:
                        return api_key
        except Exception:
            pass
        
        return None
    
    def init_database(self):
        '''Initialize SQLite database for caching descriptions with proper migration'''
        with sqlite3.connect(self.db_path) as conn:
            # Create basic table first
            conn.execute('''
                CREATE TABLE IF NOT EXISTS mod_descriptions (
                    mod_id TEXT PRIMARY KEY,
                    description TEXT,
                    category TEXT,
                    fetched_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Check and add columns if missing
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(mod_descriptions)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'source' not in columns:
                print("Adding source column to existing database...")
                conn.execute('ALTER TABLE mod_descriptions ADD COLUMN source TEXT DEFAULT "web"')
            
            if 'category' not in columns:
                print("Adding category column to existing database...")
                conn.execute('ALTER TABLE mod_descriptions ADD COLUMN category TEXT')
            
            if 'last_accessed' not in columns:
                print("Adding last_accessed column to existing database...")
                conn.execute('ALTER TABLE mod_descriptions ADD COLUMN last_accessed TIMESTAMP')
                conn.execute('UPDATE mod_descriptions SET last_accessed = fetched_date WHERE last_accessed IS NULL')
            
            # Add index for performance
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_mod_id ON mod_descriptions(mod_id)
            ''')
            
            # Create table to track request history if missing
            conn.execute('''
                CREATE TABLE IF NOT EXISTS request_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mod_id TEXT,
                    request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source TEXT,
                    success BOOLEAN,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
    
    def extract_mod_id_from_filename(self, filename: str) -> Optional[str]:
        '''Extract mod ID from filename like "ModName-9963-version.zip"'''
        patterns = [
            r'-(\d{3,6})-',     # Main pattern: -9963-, -10321-
            r'-(\d{3,6})\.zip', # Ending pattern: -9963.zip
            r'-(\d{3,6})\.rar', # Ending pattern: -9963.rar
            r'-(\d{3,6})\.7z',  # Ending pattern: -9963.7z
            r'_(\d{3,6})-',     # Pattern with underscore: _9963-
            r'_(\d{3,6})\.',    # Pattern with underscore ending: _9963.zip
            r'\[(\d{3,6})\]',   # Pattern with brackets: [9963]
            r'mod(\d{3,6})',    # Pattern with mod prefix: mod9963
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                mod_id = match.group(1)
                # Validate mod ID (must be a number and in reasonable range)
                if mod_id.isdigit() and 100 <= int(mod_id) <= 999999:
                    return mod_id
        
        return None
    
    def get_cached_description_and_category(self, mod_id: str) -> Tuple[Optional[str], Optional[str]]:
        '''Get description and category from cache if available'''
        with sqlite3.connect(self.db_path) as conn:
            # Update last_accessed
            conn.execute(
                'UPDATE mod_descriptions SET last_accessed = CURRENT_TIMESTAMP WHERE mod_id = ?',
                (mod_id,)
            )
            
            # Get description and category
            cursor = conn.execute(
                'SELECT description, category FROM mod_descriptions WHERE mod_id = ?',
                (mod_id,)
            )
            result = cursor.fetchone()
            if result:
                return result[0], result[1]
            return None, None
    

    def _prepare_description(self, raw_desc: str) -> str:
            """Prepare description with proper sanitization"""
            if not raw_desc:
                return "No description available"
                
            from src.util.text_sanitize import sanitize_text_for_ui
            
            return sanitize_text_for_ui(
                raw_desc,
                allow_unicode_letters=True,   # Keep Unicode for international descriptions
                collapse_whitespace=True,
                ascii_fallback=False,         # Don't force ASCII conversion
                xml_escape=False,             # Don't escape for display, only for XML storage
                max_length=5000,              # Reasonable limit for descriptions
            )

    def _prepare_category(self, raw_cat: str) -> str:
        """Prepare category with proper sanitization"""
        if not raw_cat:
            return "Miscellaneous"
            
        from src.util.text_sanitize import sanitize_text_for_ui
        
        return sanitize_text_for_ui(
            raw_cat,
            allow_unicode_letters=False, 
            collapse_whitespace=True,
            ascii_fallback=False,
            xml_escape=False,
            max_length=500 
        )


    def cache_description_and_category(self, mod_id, description, category, source='web', success=True):
        """Cache description and category with proper sanitization"""
        clean_desc = self._prepare_description(description or "")
        raw_cat = category or "Miscellaneous"
        clean_cat = self._prepare_category(raw_cat)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO mod_descriptions 
                (mod_id, description, category, source, last_accessed, fetched_date) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)''',
                (mod_id, clean_desc, clean_cat, source)
            )
            
            # Log request
            try:
                conn.execute(
                    'INSERT INTO request_log (mod_id, source, success) VALUES (?, ?, ?)',
                    (mod_id, source, success)
                )
            except sqlite3.OperationalError:
                # request_log table does not exist, skip logging
                pass
            
            conn.commit()
    
    def get_description_and_category_via_api(self, mod_id: str) -> Tuple[Optional[str], Optional[str], str]:
            '''Fetch description and category from Nexus API'''
            if not self.nexus_api or self.api_status != "available":
                return None, None, "API not available"
            
            try:
                print(f"Fetching mod {mod_id} info from Nexus API...")
                api_data = self.nexus_api.get_mod_info(mod_id)
                
                if api_data:
                    # Extract description and category using the API data
                    raw_desc = self.nexus_api.extract_description_from_api_data(api_data)
                    raw_cat = self.nexus_api.extract_category_from_api_data(api_data)
                    
                    # Sanitize the extracted data
                    description = self._prepare_description(raw_desc)
                    category = self._prepare_category(raw_cat)
                    
                    return description, category, "success"
                else:
                    return None, None, "Mod not found on Nexus"
                    
            except Exception as e:
                error_msg = str(e)
                print(f"API Error: {error_msg}")
                
                # If API key error, mark API as unavailable
                if "API key" in error_msg or "401" in error_msg or "403" in error_msg:
                    self.api_status = "invalid"
                
                return None, None, error_msg
    
    def fetch_description_and_category_from_web(self, mod_id: str) -> Tuple[Optional[str], Optional[str]]:
        '''Fetch description and category from web with safe scraping'''
        try:
            # Use safe web scraper
            page_content = self.web_scraper.fetch_page(mod_id)
            
            if not page_content:
                return None, None
            
            soup = BeautifulSoup(page_content, 'html.parser')
            description = self._extract_description_from_soup(soup)
            category = self._extract_category_from_soup(soup)
            
            if description and description != "Description not found":
                self.cache_description_and_category(mod_id, description, category, "web", True)
                return description, category
            else:
                self.cache_description_and_category(mod_id, "No description available", category, "web", False)
                return "No description available", category
                
        except Exception as e:
            print(f"Unexpected error in web scraping for mod {mod_id}: {e}")
            return None, None
    
    def _extract_description_from_soup(self, soup: BeautifulSoup) -> str:
        '''Extract description from parsed HTML with multiple fallback strategies'''
        
        # Strategy 1: Find description by xpath structure
        section = soup.find('div', {'id': 'section'})
        if section:
            try:
                target_div = section
                path_elements = ['div', 'div', 'div', 'div', 'div', 'div']
                indices = [None, 1, 1, None, 1, 0]
                
                for element, index in zip(path_elements, indices):
                    if index is not None:
                        divs = target_div.find_all(element, recursive=False)
                        if len(divs) > index:
                            target_div = divs[index]
                        else:
                            target_div = None
                            break
                    else:
                        target_div = target_div.find(element)
                        if not target_div:
                            break
                
                if target_div:
                    description_p = target_div.find('p')
                    if description_p:
                        text = description_p.get_text(strip=True)
                        if text and len(text) > 10:  # Ensure meaningful content
                            return text
            except Exception:
                pass
        
        # Strategy 2: Find in meta description
        description_meta = soup.find('meta', {'name': 'description'})
        if description_meta:
            content = description_meta.get('content', '').strip()
            if content and len(content) > 10:
                return content
        
        # Strategy 3: Find in summary section
        summary_section = soup.find('div', class_='summary')
        if summary_section:
            summary_p = summary_section.find('p')
            if summary_p:
                text = summary_p.get_text(strip=True)
                if text and len(text) > 10:
                    return text
        
        # Strategy 4: Find description class
        desc_div = soup.find('div', class_='description')
        if desc_div:
            text = desc_div.get_text(strip=True)
            if text and len(text) > 10:
                return text
        
        # Strategy 5: Find in mod-description or mod-summary
        for class_name in ['mod-description', 'mod-summary', 'content-description']:
            desc_elem = soup.find('div', class_=class_name)
            if desc_elem:
                text = desc_elem.get_text(strip=True)
                if text and len(text) > 10:
                    return text
        
        return "Description not found"
    
    def _extract_category_from_soup(self, soup: BeautifulSoup) -> str:
        '''Extract category from parsed HTML'''
        try:
            # Strategy 1: Find by xpath - //*[@id="breadcrumb"]/li[4]/a
            breadcrumb = soup.find('ul', {'id': 'breadcrumb'})
            if breadcrumb:
                li_elements = breadcrumb.find_all('li')
                if len(li_elements) >= 4:
                    category_link = li_elements[3].find('a')
                    if category_link:
                        category_text = category_link.get_text(strip=True)
                        if category_text:
                            return self.web_scraper.category_manager.normalize_category_name(category_text)
            
            # Strategy 2: Find by breadcrumb class
            breadcrumb_nav = soup.find('nav', class_='breadcrumb')
            if not breadcrumb_nav:
                breadcrumb_nav = soup.find('div', class_='breadcrumb')
            
            if breadcrumb_nav:
                category_links = breadcrumb_nav.find_all('a')
                for link in category_links:
                    href = link.get('href', '')
                    if 'categoryName=' in href or 'category' in href.lower():
                        category_text = link.get_text(strip=True)
                        if category_text and len(category_text) > 2:
                            return self.web_scraper.category_manager.normalize_category_name(category_text)
            
            # Strategy 3: Find by pattern in href
            all_links = soup.find_all('a')
            for link in all_links:
                href = link.get('href', '')
                if 'categoryName=' in href:
                    # Extract category from URL parameter
                    import urllib.parse
                    parsed_url = urllib.parse.urlparse(href)
                    query_params = urllib.parse.parse_qs(parsed_url.query)
                    if 'categoryName' in query_params:
                        category_name = query_params['categoryName'][0]
                        # URL decode and replace + with space
                        category_name = urllib.parse.unquote_plus(category_name)
                        return self.web_scraper.category_manager.normalize_category_name(category_name)
            
            # Strategy 4: Fallback - find by text content matching
            for link in all_links:
                text = link.get_text(strip=True)
                href = link.get('href', '')
                if ('mods' in href and any(keyword in text.lower() for keyword in 
                    ['models', 'textures', 'armor', 'weapons', 'gameplay', 'graphics', 'combat', 'misc'])):
                    return self.web_scraper.category_manager.normalize_category_name(text)
        
        except Exception as e:
            print(f"Error extracting category from web: {e}")
        
        return "Miscellaneous"
    
    def get_description_and_category(self, mod_id: str, output_callback=None) -> Tuple[str, str]:
        '''Get description and category with comprehensive error handling and API priority'''
        if not mod_id:
            return "No mod ID available", "Miscellaneous"
        
        if not mod_id.isdigit():
            return "Invalid mod ID format", "Miscellaneous"
        
        # Check cache first
        cached_desc, cached_cat = self.get_cached_description_and_category(mod_id)
        if cached_desc and cached_cat:
            if output_callback:
                output_callback(f"✓ Using cached description and category for mod {mod_id}")
            return cached_desc, cached_cat
        
        # Print API status message
        if output_callback:
            if self.api_status == "available":
                output_callback("✓ Nexus API available, using API...")
            elif self.api_status == "invalid":
                output_callback("✗ API key is invalid, switching to safe web scraping...")
            elif self.api_status == "unavailable":
                output_callback("ℹ Nexus API is not configured:")
                output_callback("  • Set environment variable NEXUS_API_KEY")
                output_callback(f"  • Or create api_key.txt file in folder {getProgramRootFolder()}/api/")
                output_callback("  Using safe web scraping...")
        
        # Try API first if available
        if self.api_status == "available":
            description, category, status = self.get_description_and_category_via_api(mod_id)
            if description and category:
                self.cache_description_and_category(mod_id, description, category, "api", True)
                if output_callback:
                    output_callback(f"✓ Successfully fetched description and category from API")
                return description, category
            else:
                if output_callback:
                    output_callback(f"✗ API failed: {status}, switching to safe web scraping...")
        
        # Fallback to safe web scraping
        if output_callback:
            health = self.web_scraper.get_health_status()
            output_callback(f"Web scraper status: {health['status']} "
                          f"(errors: {health['consecutive_errors']}, "
                          f"recent requests: {health['requests_last_5min']})")
        
        description, category = self.fetch_description_and_category_from_web(mod_id)
        if description:
            if output_callback:
                output_callback(f"✓ Successfully fetched description and category from safe web scraping")
            return description, category or "Miscellaneous"
        else:
            if output_callback:
                output_callback(f"✗ Could not fetch description after both API and web scraping attempts")
            return "Failed to fetch description from both API and web scraping", "Miscellaneous"
    
    # Backward compatibility methods
    def get_cached_description(self, mod_id: str) -> Optional[str]:
        '''Backward compatibility - get only description from cache'''
        desc, _ = self.get_cached_description_and_category(mod_id)
        return desc
    
    def cache_description(self, mod_id: str, description: str, source: str = 'web', success: bool = True):
        '''Backward compatibility - cache only description'''
        self.cache_description_and_category(mod_id, description, "Miscellaneous", source, success)
    
    def get_description(self, mod_id: str, output_callback=None) -> str:
        '''Backward compatibility - get only description'''
        desc, _ = self.get_description_and_category(mod_id, output_callback)
        return desc
    
    def get_nexus_url(self, mod_id: str) -> str:
        '''Get Nexus Mods URL for the mod'''
        if not mod_id:
            return ""
        return f"{self.base_url}{mod_id}"
    
    def get_request_stats(self) -> dict:
        '''Get statistics about requests made'''
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                    COUNT(DISTINCT mod_id) as unique_mods,
                    SUM(CASE WHEN source = 'api' THEN 1 ELSE 0 END) as api_requests,
                    SUM(CASE WHEN source = 'web' THEN 1 ELSE 0 END) as web_requests
                FROM request_log 
                WHERE request_time > datetime('now', '-24 hours')
            ''')
            
            result = cursor.fetchone()
            stats = {
                'total_requests_24h': result[0] or 0,
                'successful_requests_24h': result[1] or 0,
                'unique_mods_24h': result[2] or 0,
                'api_requests_24h': result[3] or 0,
                'web_requests_24h': result[4] or 0
            }
            
            # Add web scraper health info
            if hasattr(self, 'web_scraper'):
                stats.update(self.web_scraper.get_health_status())
            
            return stats
    
    def cleanup_old_cache(self, days_old: int = 30):
        '''Clean up old cached entries'''
        with sqlite3.connect(self.db_path) as conn:
            # Delete old entries based on last_accessed
            deleted = conn.execute('''
                DELETE FROM mod_descriptions 
                WHERE last_accessed < datetime('now', '-{} days')
            '''.format(days_old)).rowcount
            
            # Clean up request log if table exists
            try:
                log_deleted = conn.execute('''
                    DELETE FROM request_log 
                    WHERE request_time < datetime('now', '-{} days')
                '''.format(days_old)).rowcount
            except sqlite3.OperationalError:
                log_deleted = 0
            
            conn.commit()
            print(f"Cleaned up {deleted} cache entries and {log_deleted} log entries older than {days_old} days")
    
    def reset_scraper_if_needed(self):
        '''Reset web scraper if too many consecutive errors'''
        if hasattr(self, 'web_scraper'):
            health = self.web_scraper.get_health_status()
            if health['consecutive_errors'] > 5:
                print("Resetting web scraper due to consecutive errors...")
                self.web_scraper = SafeWebScraper(self.base_url)
    
    def get_detailed_status(self) -> dict:
        '''Get detailed information about fetcher status'''
        status = {
            'api_status': self.api_status,
            'api_available': self.api_status == "available",
            'web_scraper_available': hasattr(self, 'web_scraper'),
            'database_path': self.db_path,
            'base_url': self.base_url,
        }
        
        # Add web scraper info
        if hasattr(self, 'web_scraper'):
            status['web_scraper_health'] = self.web_scraper.get_health_status()
        
        # Add database info
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM mod_descriptions')
                status['cached_descriptions'] = cursor.fetchone()[0]
        except Exception:
            status['cached_descriptions'] = 0
        
        return status
