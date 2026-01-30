#!/usr/bin/env python3
"""
DNS Sync Script for dnsmasq
Fetches blocked sites from NetGarde API and updates dnsmasq configuration.
"""

import os
import sys
import subprocess
import time
import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
API_ENDPOINT = os.getenv('API_ENDPOINT', '/blocked-sites')
BLOCK_IP = os.getenv('BLOCK_IP', '0.0.0.0')  # IP to redirect blocked domains to
DNS_CONFIG_PATH = os.getenv('DNS_CONFIG_PATH', '/etc/dnsmasq.d/blocked-domains.conf')
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '3600'))  # Default: 1 hour
DNSMASQ_RESTART_CMD = os.getenv('DNSMASQ_RESTART_CMD', 'killall -HUP dnsmasq')
PAGE_SIZE = int(os.getenv('PAGE_SIZE', '100'))  # Max items per page


def fetch_blocked_sites_from_api(api_url: str, endpoint: str, page_size: int = 100) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch all blocked sites from the NetGarde API.
    Handles pagination to get all blocked sites.
    Returns a list of blocked site dictionaries.
    """
    if not api_url:
        logger.error("API_BASE_URL environment variable is not set")
        return None
    
    try:
        import urllib.request
        import urllib.parse
        
        all_blocked_sites = []
        page = 1
        
        while True:
            # Build URL with pagination
            params = {'page': page, 'page_size': page_size}
            url = f"{api_url.rstrip('/')}{endpoint}?{urllib.parse.urlencode(params)}"
            
            logger.info(f"Fetching blocked sites from {url} (page {page})")
            
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    logger.error(f"API returned status {response.status}")
                    return None
                
                data = json.loads(response.read().decode('utf-8'))
                
                # Handle paginated response
                if 'items' in data:
                    items = data['items']
                    total = data.get('total', 0)
                    logger.info(f"Fetched {len(items)} blocked sites (page {page}, total: {total})")
                    
                    if not items:
                        break
                    
                    all_blocked_sites.extend(items)
                    
                    # Check if there are more pages
                    if len(all_blocked_sites) >= total or len(items) < page_size:
                        break
                    
                    page += 1
                else:
                    # Non-paginated response (array)
                    if isinstance(data, list):
                        all_blocked_sites = data
                        break
                    else:
                        logger.error("Unexpected API response format")
                        return None
        
        logger.info(f"Total blocked sites fetched: {len(all_blocked_sites)}")
        return all_blocked_sites
        
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP error fetching blocked sites: {e.code} - {e.reason}")
        return None
    except urllib.error.URLError as e:
        logger.error(f"URL error fetching blocked sites: {e.reason}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching blocked sites: {e}", exc_info=True)
        return None


def convert_to_dnsmasq_format(blocked_sites: List[Dict[str, Any]], block_ip: str = '0.0.0.0') -> List[str]:
    """
    Convert blocked sites from API format to dnsmasq format.
    Returns a list of dnsmasq configuration lines.
    """
    entries = []
    
    for site in blocked_sites:
        domain = site.get('domain', '').strip()
        if not domain:
            continue
        
        # Skip deleted sites
        if site.get('is_deleted', False):
            continue
        
        # Normalize domain (remove protocol, www, etc.)
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0]  # Remove paths
        domain = domain.split('?')[0]  # Remove query strings
        
        if not domain:
            continue
        
        # Create dnsmasq entry to block the domain
        # Format: address=/domain.com/0.0.0.0
        entry = f"address=/{domain}/{block_ip}"
        entries.append(entry)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_entries = []
    for entry in entries:
        if entry not in seen:
            seen.add(entry)
            unique_entries.append(entry)
    
    logger.info(f"Converted {len(blocked_sites)} blocked sites to {len(unique_entries)} unique dnsmasq entries")
    return unique_entries


def write_dns_config(entries: List[str], config_path: str) -> bool:
    """
    Write DNS entries to dnsmasq configuration file.
    """
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write header
        content = f"# Auto-generated DNS configuration\n"
        content += f"# Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Write entries
        for entry in entries:
            content += f"{entry}\n"
        
        # Write to file
        config_file.write_text(content)
        logger.info(f"Wrote {len(entries)} entries to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing DNS config: {e}")
        return False


def reload_dnsmasq(restart_cmd: str) -> bool:
    """
    Reload dnsmasq configuration.
    """
    if not restart_cmd or not restart_cmd.strip():
        logger.info("DNSMASQ_RESTART_CMD is empty, skipping reload (host script will handle it)")
        return True
    
    try:
        logger.info("Reloading dnsmasq...")
        result = subprocess.run(
            restart_cmd.split(),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            logger.info("dnsmasq reloaded successfully")
            return True
        else:
            logger.warning(f"dnsmasq reload command returned non-zero: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error reloading dnsmasq: {e}")
        return False


def sync_dns():
    """
    Main sync function.
    """
    logger.info("Starting DNS sync...")
    
    # Fetch blocked sites from API
    blocked_sites = fetch_blocked_sites_from_api(API_BASE_URL, API_ENDPOINT, PAGE_SIZE)
    if blocked_sites is None:
        logger.error("Failed to fetch blocked sites from API")
        return False
    
    if not blocked_sites:
        logger.warning("No blocked sites to sync")
        return False
    
    # Convert to dnsmasq format
    entries = convert_to_dnsmasq_format(blocked_sites, BLOCK_IP)
    if not entries:
        logger.warning("No DNS entries generated from blocked sites")
        return False
    
    # Write configuration
    if not write_dns_config(entries, DNS_CONFIG_PATH):
        logger.error("Failed to write DNS configuration")
        return False
    
    # Reload dnsmasq (skip if DNSMASQ_RESTART_CMD is empty - host script will handle it)
    if DNSMASQ_RESTART_CMD:
        if not reload_dnsmasq(DNSMASQ_RESTART_CMD):
            logger.warning("Failed to reload dnsmasq, but config was updated")
            return False
    else:
        logger.info("Skipping dnsmasq reload (will be done on host)")
    
    logger.info("DNS sync completed successfully")
    return True


def main():
    """
    Main entry point.
    """
    logger.info("DNS Sync Container Started")
    logger.info(f"Configuration:")
    logger.info(f"  API_BASE_URL: {API_BASE_URL}")
    logger.info(f"  API_ENDPOINT: {API_ENDPOINT}")
    logger.info(f"  BLOCK_IP: {BLOCK_IP}")
    logger.info(f"  DNS_CONFIG_PATH: {DNS_CONFIG_PATH}")
    logger.info(f"  SYNC_INTERVAL: {SYNC_INTERVAL} seconds")
    logger.info(f"  PAGE_SIZE: {PAGE_SIZE}")
    logger.info(f"  DNSMASQ_RESTART_CMD: {DNSMASQ_RESTART_CMD}")
    
    # Run once immediately
    sync_dns()
    
    # Then run on interval
    if SYNC_INTERVAL > 0:
        logger.info(f"Starting periodic sync (every {SYNC_INTERVAL} seconds)")
        while True:
            time.sleep(SYNC_INTERVAL)
            sync_dns()
    else:
        logger.info("SYNC_INTERVAL is 0, running once and exiting")
        sys.exit(0 if sync_dns() else 1)


if __name__ == '__main__':
    main()
