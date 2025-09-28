import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import asyncio
import aiofiles
from models import Account, AccountStatus

class AccountManager:
    def __init__(self, accounts_path: str):
        self.accounts_path = Path(accounts_path)
        self.accounts_file = self.accounts_path / "accounts.txt"
        
    async def parse_accounts_file(self) -> Dict[str, dict]:
        """Parse POL accounts.txt file"""
        accounts = {}
        
        if not self.accounts_file.exists():
            return accounts
            
        try:
            async with aiofiles.open(self.accounts_file, 'r') as f:
                content = await f.read()
                
            # POL accounts.txt format parsing
            current_account = None
            for line in content.split('\n'):
                line = line.strip()
                
                if not line:
                    continue
                    
                # Account header
                if line.startswith('Account'):
                    match = re.match(r'Account\s+(\w+)', line)
                    if match:
                        current_account = match.group(1)
                        accounts[current_account] = {
                            'username': current_account,
                            'properties': {},
                            'characters': []
                        }
                
                # Account properties
                elif current_account and '\t' in line:
                    parts = line.split('\t', 1)
                    if len(parts) == 2:
                        key, value = parts
                        accounts[current_account]['properties'][key.strip()] = value.strip()
                        
        except Exception as e:
            print(f"Error parsing accounts file: {e}")
            
        return accounts
    
    async def save_accounts_file(self, accounts: Dict[str, dict]):
        """Save accounts to POL format"""
        content = []
        
        for username, account_data in accounts.items():
            content.append(f"Account {username}")
            content.append("{")
            
            # Save properties
            for key, value in account_data['properties'].items():
                content.append(f"\t{key}\t{value}")
                
            content.append("}")
            content.append("")
            
        async with aiofiles.open(self.accounts_file, 'w') as f:
            await f.write('\n'.join(content))
    
    async def list_accounts(self) -> List[dict]:
        """List all accounts"""
        accounts = await self.parse_accounts_file()
        
        account_list = []
        for username, data in accounts.items():
            props = data['properties']
            account_list.append({
                'username': username,
                'email': props.get('EMail', ''),
                'cmdlevel': int(props.get('DefaultCmdLevel', 0)),
                'expansion': props.get('UOExpansion', 'ML'),
                'status': props.get('Status', 'active'),
                'created_at': props.get('Created', ''),
                'last_login': props.get('LastLogin', ''),
                'character_count': len(data.get('characters', []))
            })
            
        return account_list
    
    async def get_account(self, username: str) -> Optional[dict]:
        """Get specific account details"""
        accounts = await self.parse_accounts_file()
        
        if username not in accounts:
            return None
            
        data = accounts[username]
        props = data['properties']
        
        return {
            'username': username,
            'email': props.get('EMail', ''),
            'cmdlevel': int(props.get('DefaultCmdLevel', 0)),
            'expansion': props.get('UOExpansion', 'ML'),
            'status': props.get('Status', 'active'),
            'created_at': props.get('Created', ''),
            'last_login': props.get('LastLogin', ''),
            'characters': data.get('characters', []),
            'properties': props
        }
    
    async def create_account(self, account: Account) -> dict:
        """Create a new account"""
        accounts = await self.parse_accounts_file()
        
        if account.username in accounts:
            return {"success": False, "error": "Account already exists"}
        
        # Create account entry
        accounts[account.username] = {
            'username': account.username,
            'properties': {
                'Password': account.password,  # In production, this should be hashed
                'EMail': account.email or '',
                'DefaultCmdLevel': str(account.cmdlevel),
                'UOExpansion': account.expansion,
                'Status': account.status.value,
                'Created': datetime.now().isoformat(),
                'LastLogin': '',
                'ACTUsed': '0'
            },
            'characters': []
        }
        
        await self.save_accounts_file(accounts)
        return {"success": True}
    
    async def update_account(self, username: str, account: Account) -> dict:
        """Update an existing account"""
        accounts = await self.parse_accounts_file()
        
        if username not in accounts:
            return {"success": False, "error": "Account not found"}
        
        # Update account properties
        props = accounts[username]['properties']
        
        if account.password:
            props['Password'] = account.password
        if account.email is not None:
            props['EMail'] = account.email
        if account.cmdlevel is not None:
            props['DefaultCmdLevel'] = str(account.cmdlevel)
        if account.expansion:
            props['UOExpansion'] = account.expansion
        if account.status:
            props['Status'] = account.status.value
            
        await self.save_accounts_file(accounts)
        return {"success": True}
    
    async def delete_account(self, username: str) -> dict:
        """Delete an account"""
        accounts = await self.parse_accounts_file()
        
        if username not in accounts:
            return {"success": False, "error": "Account not found"}
        
        del accounts[username]
        
        await self.save_accounts_file(accounts)
        return {"success": True}
    
    async def ban_account(self, username: str) -> dict:
        """Ban an account"""
        accounts = await self.parse_accounts_file()
        
        if username not in accounts:
            return {"success": False, "error": "Account not found"}
        
        accounts[username]['properties']['Status'] = 'banned'
        
        await self.save_accounts_file(accounts)
        return {"success": True}
    
    async def unban_account(self, username: str) -> dict:
        """Unban an account"""
        accounts = await self.parse_accounts_file()
        
        if username not in accounts:
            return {"success": False, "error": "Account not found"}
        
        accounts[username]['properties']['Status'] = 'active'
        
        await self.save_accounts_file(accounts)
        return {"success": True}