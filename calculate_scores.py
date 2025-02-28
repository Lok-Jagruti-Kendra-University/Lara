import requests
import os
import pandas as pd
from bs4 import BeautifulSoup

GITHUB_ORG = "Lok-Jagruti-Kendra-University"
GITHUB_TOKEN = "my-ljku-artifacts-token"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

#print(pd.__version__)

def fetch_sonarcloud_score():
    """Fetch SonarCloud quality metrics."""
    url = "https://sonarcloud.io/api/measures/component"
    params = {
        "component": "Lok-Jagruti-Kendra-University_Lara",  # Your SonarCloud project key
        "branch":"main",
        "ps":1000,
        "metricKeys": "coverage, ncloc, files, statements, vulnerabilities, bugs, code_smells, security_hotspots, duplicated_lines_density, cognitive_complexity, security_rating, sqale_rating, reliability_rating"
    }
    response = requests.get(url, params=params)
    # Debugging output
    
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)  
    
    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return None

    data = response.json()
    measures = data.get("component", {}).get("measures", [])

    # Extract metrics
    scores = {m["metric"]: m["value"] for m in measures}
        
    print(scores)
    
    if response.status_code == 200:
        data = response.json()
        measures = data.get("component", {}).get("measures", [])

        # SonarCloud Evaluation Formula
        code_smells_count = float(next((m["value"] for m in measures if m["metric"] == "code_smells"), 0))
        bugs_count = float(next((m["value"] for m in measures if m["metric"] == "bugs"), 0))
        vulnerabilities_count = float(next((m["value"] for m in measures if m["metric"] == "vulnerabilities"), 0))
        duplicated_lines_percentage = float(next((m["value"] for m in measures if m["metric"] == "duplicated_lines_density"), 0))
        total_files = float(next((m["value"] for m in measures if m["metric"] == "files"), 0))
        
        ## Metrics and Weights
        #- **Code Coverage**: 30%
        #  coverage_score = (coverage_percentage / 100) * 30
        #- **Bugs**: 30%
        bugs_score = (1 - (bugs_count / total_files)) * 30
        #- **Vulnerabilities**: 30%
        vulnerabilities_score = (1 - (vulnerabilities_count / total_files)) * 30
        #- **Code Smells**: 25%
        code_smells_score = (1 - (code_smells_count / total_files)) * 25
        #- **Duplicated Lines**: 15%
        duplicated_lines_score = (1 - (duplicated_lines_percentage / 100)) * 15
        
        ## Final Score Calculation
        final_score = bugs_score + vulnerabilities_score + code_smells_score + duplicated_lines_score  #coverage_score + 
        scores["Final Score"] = final_score;
        
        return scores;
        
        # Example: Extracting coverage score
        code_smells = next((m["value"] for m in measures if m["metric"] == "code_smells"), 0)
        return float(code_smells)
    
    return 0  # Default to 0 if request fails

# SonarCloud Summary Page URL
SONARCLOUD_URL = "https://sonarcloud.io/summary/overall?id=Lok-Jagruti-Kendra-University_PHPDemo&branch=main"

def save_to_excel(data):
    if not data:
        print("No data to save")
        return
    df = pd.DataFrame([data])
    df.to_excel("sonarcloud_summary.xlsx", index=False)
    print("Saved to sonarcloud_summary.xlsx")

def get_repositories():
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/repos"
    response = requests.get(url, headers=HEADERS)
    return [repo["name"] for repo in response.json()]

def get_latest_workflow_run(repo):
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{repo}/actions/runs"
    response = requests.get(url, headers=HEADERS)
    runs = response.json().get("workflow_runs", [])
    return runs[0]["id"] if runs else None

def download_artifact(repo, run_id):
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{repo}/actions/runs/{run_id}/artifacts"
    response = requests.get(url, headers=HEADERS)
    artifacts = response.json().get("artifacts", [])
    
    if artifacts:
        artifact_url = artifacts[0]["archive_download_url"]
        response = requests.get(artifact_url, headers=HEADERS)
        
        with open(f"artifacts/{repo}.zip", "wb") as file:
            file.write(response.content)
        print(f"Downloaded artifacts for {repo}")
    else:
        print(f"No artifacts found for {repo}")

if __name__ == "__main__":
    #summary_data = fetch_sonarcloud_summary()
    data = fetch_sonarcloud_score()
    save_to_excel(data)

    #scores = aggregate_scores()
    #print("Aggregated Scores:", scores)
