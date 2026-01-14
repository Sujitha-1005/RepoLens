import requests
import base64
import os
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
headers = {"Authorization": f"token {GITHUB_TOKEN}"}

def fetch_github_file(owner, repo, path):
    """Utility to fetch raw content of a specific file."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        try:
            return base64.b64decode(data['content']).decode('utf-8')
        except:
            return None
    return None

def get_repo_stats(owner, repo):
    """Fetch repository statistics from GitHub API"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    return None

def get_commit_activity(owner, repo):
    """Get recent commit activity"""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    res = requests.get(url, headers=headers, params={'per_page': 10})
    if res.status_code == 200:
        commits = res.json()
        if commits:
            last_commit_date = commits[0]['commit']['author']['date']
            return {
                'last_commit': last_commit_date,
                'recent_commits': len(commits)
            }
    return None

def get_contributors(owner, repo):
    """Get contributor information"""
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    res = requests.get(url, headers=headers, params={'per_page': 5})
    if res.status_code == 200:
        contributors = res.json()
        return [{'login': c['login'], 'contributions': c['contributions'], 'avatar_url': c['avatar_url']} for c in contributors[:5]]
    return []

def get_languages(owner, repo):
    """Get language breakdown"""
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    return {}

def get_issues_stats(owner, repo):
    """Get issues and PR statistics"""
    repo_url = f"https://api.github.com/repos/{owner}/{repo}"
    issues_url = f"{repo_url}/issues"
    
    # Get open issues
    open_issues = requests.get(issues_url, headers=headers, params={'state': 'open', 'per_page': 1})
    
    stats = {}
    if 'Link' in open_issues.headers:
        # Parse the Link header to get total count
        link = open_issues.headers['Link']
        if 'last' in link:
            try:
                stats['open_issues'] = int(link.split('page=')[-1].split('>')[0])
            except:
                 stats['open_issues'] = len(open_issues.json())
        else:
            stats['open_issues'] = len(open_issues.json())
    else:
         # If no link header and status is 200, use length. If 404/etc, 0.
        if open_issues.status_code == 200:
            stats['open_issues'] = len(open_issues.json())
        else:
            stats['open_issues'] = 0
            
    return stats

def get_releases(owner, repo):
    """Get release information"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    res = requests.get(url, headers=headers, params={'per_page': 5})
    if res.status_code == 200:
        releases = res.json()
        return [{
            'tag': r['tag_name'],
            'name': r['name'],
            'published_at': r['published_at'],
            'html_url': r['html_url']
        } for r in releases[:5]]
    return []

def check_repo_health(owner, repo):
    """Check for repository health indicators"""
    health = {}
    
    # Check for CI/CD
    workflows_url = f"https://api.github.com/repos/{owner}/{repo}/actions/workflows"
    workflows = requests.get(workflows_url, headers=headers)
    health['has_ci_cd'] = workflows.status_code == 200 and len(workflows.json().get('workflows', [])) > 0
    
    # Check for common files
    health['has_license'] = fetch_github_file(owner, repo, 'LICENSE') is not None
    health['has_contributing'] = fetch_github_file(owner, repo, 'CONTRIBUTING.md') is not None
    health['has_gitignore'] = fetch_github_file(owner, repo, '.gitignore') is not None
    
    return health

def calculate_maintenance_status(last_commit_date):
    """Calculate if repo is actively maintained"""
    try:
        commit_date = datetime.strptime(last_commit_date, '%Y-%m-%dT%H:%M:%SZ')
        days_since = (datetime.utcnow() - commit_date).days
        
        if days_since < 30:
            return "Active"
        elif days_since < 90:
            return "Recently Updated"
        elif days_since < 365:
            return "Sporadic"
        else:
            return "Inactive"
    except:
        return "Unknown"

def format_number(num):
    """Format large numbers for readability"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

def analyze_repo_ai(owner, repo, repo_url):
    """Use Gemini to analyze the repository"""
    readme = fetch_github_file(owner, repo, "README.md") or ""

    tech_data = ""
    for dep_file in ["package.json", "requirements.txt", "go.mod", "pom.xml", "Gemfile"]:
        content = fetch_github_file(owner, repo, dep_file)
        if content:
            tech_data += f"\n--- FOUND {dep_file} ---\n{content[:2000]}\n"

    prompt = f"""
    Analyze this GitHub repository: {repo_url}
    
    README DATA: {readme[:3000]}
    
    DEPENDENCY/CONFIG FILES:
    {tech_data}

    Provide the output in valid JSON format with the following keys:
    - summary: Plain-English Explanation (string)
    - tech_stack: List of frameworks/libraries (list of strings)
    - setup_difficulty: Score 1-10 (integer)
    - setup_reasoning: Reasoning for the score (string)
    - beginner_friendly: Easy/Medium/Hard (string)
    - similar_projects: List of 3 real-world equivalents (list of strings)
    - key_features: List of 3-5 key features (list of strings)
    """

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
             config={
                'response_mime_type': 'application/json'
            }
        )
        import json
        return json.loads(response.text)
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "summary": f"AI Analysis Failed: {str(e)}",
            "tech_stack": ["Error"],
            "setup_difficulty": 0,
            "setup_reasoning": "Could not generate analysis.",
            "beginner_friendly": "Unknown",
            "similar_projects": [],
            "key_features": []
        }

def analyze_repo(repo_url):
    """Main function to gather all repo data"""
    try:
        parts = repo_url.strip("/").split("/")
        owner, repo = parts[-2], parts[-1]
    except:
        return {"error": "Invalid URL format"}

    stats = get_repo_stats(owner, repo)
    if not stats:
        return {"error": "Repository not found or private"}

    commit_data = get_commit_activity(owner, repo)
    maintenance = "Unknown"
    last_commit = "Unknown"
    if commit_data:
        maintenance = calculate_maintenance_status(commit_data['last_commit'])
        last_commit = commit_data['last_commit'][:10]

    languages = get_languages(owner, repo)
    # Calculate language percentages
    total_bytes = sum(languages.values())
    lang_stats = []
    if total_bytes > 0:
        for lang, count in languages.items():
            percent = (count / total_bytes) * 100
            if percent > 1: # Only show > 1%
                lang_stats.append({"name": lang, "percent": round(percent, 1)})
    
    lang_stats.sort(key=lambda x: x['percent'], reverse=True)

    contributors = get_contributors(owner, repo)
    health = check_repo_health(owner, repo)
    releases = get_releases(owner, repo)
    issues = get_issues_stats(owner, repo)

    ai_analysis = analyze_repo_ai(owner, repo, repo_url)

    return {
        "owner": owner,
        "name": repo,
        "description": stats.get("description"),
        "stars": format_number(stats.get("stargazers_count", 0)),
        "forks": format_number(stats.get("forks_count", 0)),
        "watchers": format_number(stats.get("watchers_count", 0)),
        "size": f"{stats.get('size', 0)} KB",
        "created_at": stats.get("created_at")[:10],
        "updated_at": stats.get("updated_at")[:10],
        "homepage": stats.get("homepage"),
        "license": stats.get("license", {}).get("name") if stats.get("license") else "None",
        "maintenance": maintenance,
        "last_commit": last_commit,
        "languages": lang_stats,
        "contributors": contributors,
        "health": health,
        "releases": releases,
        "open_issues": issues.get("open_issues", 0),
        "clone_url": stats.get("clone_url"),
        "ai_analysis": ai_analysis
    }

def search_repos(query):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 12 
    }
    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 200:
        data = res.json()
        results = []
        for repo in data.get("items", []):
            results.append({
                "name": repo["full_name"],
                "url": repo["html_url"],
                "stars": format_number(repo["stargazers_count"]),
                "description": repo["description"],
                "language": repo["language"],
                "updated_at": repo["updated_at"][:10],
                "owner_avatar": repo["owner"]["avatar_url"]
            })
        return results
    return []

def analyze_user(username):
    user_url = f"https://api.github.com/users/{username}"
    user_res = requests.get(user_url, headers=headers)
    if user_res.status_code != 200:
        return {"error": "User not found"}
    
    user = user_res.json()
    
    repos_url = f"https://api.github.com/users/{username}/repos"
    repos_res = requests.get(repos_url, headers=headers, params={"per_page": 100, "sort": "updated"})
    repos = repos_res.json() if repos_res.status_code == 200 else []
    
    total_stars = sum(r['stargazers_count'] for r in repos)
    
    languages = {}
    for r in repos:
        if r['language']:
            languages[r['language']] = languages.get(r['language'], 0) + 1
            
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    top_languages = [{"name": l[0], "count": l[1]} for l in top_languages]
    
    popular_repos = sorted(repos, key=lambda x: x['stargazers_count'], reverse=True)[:]
    popular_repos_data = [{
        "name": r['name'],
        "stars": format_number(r['stargazers_count']),
        "description": r['description'],
        "language": r['language'],
        "url": r['html_url']
    } for r in popular_repos]

    return {
        "name": user.get("name"),
        "username": user.get("login"),
        "bio": user.get("bio"),
        "avatar_url": user.get("avatar_url"),
        "public_repos": user.get("public_repos"),
        "followers": format_number(user.get("followers", 0)),
        "following": format_number(user.get("following", 0)),
        "total_stars": format_number(total_stars),
        "top_languages": top_languages,
        "popular_repos": popular_repos_data,
        "html_url": user.get("html_url"),
        "created_at": user.get("created_at")[:10]
    }
