"""
GitHub Tools - Search repositories and get repo information.

Uses GitHub's public API (no API key required for public repos).
Rate limit: 60 requests/hour without auth.
"""

import logging
from urllib.parse import quote_plus

from ..utils.http_client import fetch_json

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


async def search_github(
    query: str,
    num_results: int = 5,
    language: str = "",
    sort: str = "stars"
) -> str:
    """
    Search GitHub repositories.
    
    Args:
        query: Search query (keywords, topics, etc.)
        num_results: Number of results to return (default: 5, max: 10)
        language: Filter by programming language (e.g., 'python', 'javascript')
        sort: Sort by - 'stars', 'forks', 'updated', 'help-wanted-issues'
        
    Returns:
        List of matching GitHub repositories
    """
    if not query.strip():
        return "❌ Error: Please provide a search query."
    
    num_results = min(num_results, 10)
    
    # Build query
    search_query = query
    if language:
        search_query += f" language:{language}"
    
    encoded_query = quote_plus(search_query)
    
    url = f"{GITHUB_API}/search/repositories?q={encoded_query}&sort={sort}&order=desc&per_page={num_results}"
    
    data = await fetch_json(url)
    
    if not data or "items" not in data:
        return f"❌ Error: Unable to search GitHub for '{query}'."
    
    repos = data.get("items", [])
    
    if not repos:
        return f"No GitHub repositories found for: {query}"
    
    # Format output
    output = f"🐙 GitHub Search: '{query}'"
    if language:
        output += f" (Language: {language})"
    output += f"\n{'=' * 50}\n"
    
    for i, repo in enumerate(repos, 1):
        name = repo.get("full_name", "unknown")
        description = repo.get("description", "No description")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        lang = repo.get("language", "Unknown")
        html_url = repo.get("html_url", "")
        topics = repo.get("topics", [])[:3]
        
        output += f"\n{i}. **{name}**\n"
        if description:
            output += f"   📝 {description[:100]}{'...' if len(description) > 100 else ''}\n"
        output += f"   ⭐ {stars:,} | 🍴 {forks:,} | 💻 {lang}\n"
        if topics:
            output += f"   🏷️ {', '.join(topics)}\n"
        output += f"   🔗 {html_url}\n"
    
    total_count = data.get("total_count", 0)
    output += f"\n📊 Total results: {total_count:,}"
    
    return output


async def get_repo_info(repo: str) -> str:
    """
    Get detailed information about a GitHub repository.
    
    Args:
        repo: Repository in format 'owner/repo' (e.g., 'microsoft/vscode')
        
    Returns:
        Detailed repository information
    """
    if not repo.strip():
        return "❌ Error: Please provide a repository name (e.g., 'owner/repo')."
    
    repo = repo.strip()
    
    # Remove github.com URL if provided
    if "github.com/" in repo:
        repo = repo.split("github.com/")[-1]
    
    # Remove trailing slashes
    repo = repo.strip("/")
    
    # Check format
    if "/" not in repo:
        return "❌ Error: Please use format 'owner/repo' (e.g., 'microsoft/vscode')."
    
    url = f"{GITHUB_API}/repos/{repo}"
    
    data = await fetch_json(url)
    
    if not data or data.get("message") == "Not Found":
        return f"❌ Error: Repository '{repo}' not found."
    
    # Extract info
    name = data.get("full_name", repo)
    description = data.get("description", "No description")
    stars = data.get("stargazers_count", 0)
    forks = data.get("forks_count", 0)
    watchers = data.get("watchers_count", 0)
    open_issues = data.get("open_issues_count", 0)
    language = data.get("language", "Unknown")
    license_info = data.get("license", {})
    license_name = license_info.get("name", "No license") if license_info else "No license"
    html_url = data.get("html_url", "")
    homepage = data.get("homepage", "")
    topics = data.get("topics", [])
    created_at = data.get("created_at", "")[:10]
    updated_at = data.get("updated_at", "")[:10]
    default_branch = data.get("default_branch", "main")
    
    owner = data.get("owner", {})
    owner_name = owner.get("login", "unknown")
    owner_type = owner.get("type", "User")
    
    output = f"""🐙 **{name}**
{'=' * 50}

📝 {description}

📊 **Stats**
   ⭐ Stars: {stars:,}
   🍴 Forks: {forks:,}
   👁️ Watchers: {watchers:,}
   🐛 Open Issues: {open_issues:,}

💻 **Details**
   📦 Language: {language}
   📜 License: {license_name}
   🌿 Default Branch: {default_branch}
   📅 Created: {created_at}
   🔄 Last Updated: {updated_at}

👤 **Owner**: {owner_name} ({owner_type})
"""
    
    if topics:
        output += f"\n🏷️ **Topics**: {', '.join(topics)}"
    
    output += f"\n\n🔗 **Links**"
    output += f"\n   📂 Repository: {html_url}"
    if homepage:
        output += f"\n   🌐 Homepage: {homepage}"
    
    return output


async def get_github_user(username: str) -> str:
    """
    Get information about a GitHub user or organization.
    
    Args:
        username: GitHub username
        
    Returns:
        User/organization profile information
    """
    if not username.strip():
        return "❌ Error: Please provide a GitHub username."
    
    username = username.strip().lstrip("@")
    
    url = f"{GITHUB_API}/users/{username}"
    
    data = await fetch_json(url)
    
    if not data or data.get("message") == "Not Found":
        return f"❌ Error: GitHub user '{username}' not found."
    
    # Extract info
    name = data.get("name", username)
    login = data.get("login", username)
    bio = data.get("bio", "No bio")
    company = data.get("company", "")
    location = data.get("location", "")
    blog = data.get("blog", "")
    public_repos = data.get("public_repos", 0)
    followers = data.get("followers", 0)
    following = data.get("following", 0)
    user_type = data.get("type", "User")
    html_url = data.get("html_url", "")
    created_at = data.get("created_at", "")[:10]
    
    output = f"""👤 **{name}** (@{login})
{'=' * 50}

"""
    if bio:
        output += f"📝 {bio}\n\n"
    
    output += f"""📊 **Stats**
   📦 Public Repos: {public_repos}
   👥 Followers: {followers:,}
   👤 Following: {following}
   📅 Joined: {created_at}
"""
    
    if company or location:
        output += "\n📌 **Info**"
        if company:
            output += f"\n   🏢 {company}"
        if location:
            output += f"\n   📍 {location}"
    
    if blog:
        output += f"\n   🌐 {blog}"
    
    output += f"\n\n🔗 {html_url}"
    
    return output
