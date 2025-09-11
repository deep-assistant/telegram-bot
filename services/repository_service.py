import re
from typing import Optional, Dict, Any

from db import data_base, db_key


class RepositoryService:
    CURRENT_REPOSITORY_KEY = "current_repository"
    
    def get_current_repository(self, user_id: str) -> Optional[str]:
        """Get the current repository URL for a user"""
        try:
            return data_base[db_key(user_id, self.CURRENT_REPOSITORY_KEY)].decode('utf-8')
        except KeyError:
            return None

    def set_current_repository(self, user_id: str, repository_url: str):
        """Set the current repository URL for a user"""
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_REPOSITORY_KEY)] = repository_url
        data_base.commit()

    def clear_current_repository(self, user_id: str):
        """Clear the current repository for a user"""
        try:
            with data_base.transaction():
                del data_base[db_key(user_id, self.CURRENT_REPOSITORY_KEY)]
            data_base.commit()
        except KeyError:
            pass  # Repository was already not set

    def validate_github_url(self, url: str) -> bool:
        """Validate if the provided URL is a valid GitHub repository URL"""
        github_pattern = r'^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$'
        return bool(re.match(github_pattern, url))

    def parse_repository_info(self, url: str) -> Optional[Dict[str, str]]:
        """Parse GitHub repository URL to extract owner and repo name"""
        if not self.validate_github_url(url):
            return None
        
        # Remove trailing slash if present and extract components
        clean_url = url.rstrip('/')
        parts = clean_url.split('/')
        
        if len(parts) >= 5:
            owner = parts[-2]
            repo = parts[-1]
            return {
                'owner': owner,
                'repo': repo,
                'full_name': f"{owner}/{repo}",
                'url': clean_url
            }
        return None

    def format_repository_context(self, repository_url: str) -> str:
        """Format repository information for inclusion in system message"""
        repo_info = self.parse_repository_info(repository_url)
        if not repo_info:
            return ""
        
        context = f"""

REPOSITORY CONTEXT:
You are working with the GitHub repository: {repo_info['full_name']}
Repository URL: {repo_info['url']}

When answering questions, consider this repository context and provide relevant code examples, explanations, or suggestions specific to this project when appropriate.
"""
        return context


repositoryService = RepositoryService()