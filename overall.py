import requests
import csv

# SonarCloud API credentials
SONARCLOUD_TOKEN = "44008bdc256019db2fd5c2fc7693fb2a319dc611"
ORG_KEY = "lok-jagruti-kendra-university"
SONAR_BASE_URL = "https://sonarcloud.io/api"

# Step 1: Get all repositories in the organization
projects_url = f"{SONAR_BASE_URL}/projects/search"
params = {"organization": ORG_KEY, "ps": "500"}  # Get up to 500 repositories
headers = {"Authorization": f"Bearer {SONARCLOUD_TOKEN}"}

response = requests.get(projects_url, params=params, headers=headers)
projects_data = response.json()

# Extract project keys
projects = [p["key"] for p in projects_data.get("components", [])]

# Step 2: Get analysis data for each repository
metrics = "ncloc,coverage,files,statements,bugs,vulnerabilities,code_smells,duplicated_lines_density,cognitive_complexity,security_rating,sqale_rating,reliability_rating"
csv_file = "sonarcloud_all_projects_analysis.csv"

with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Project", "Date", "Metric", "Value"])

    for project in projects:
        analysis_url = f"{SONAR_BASE_URL}/measures/search_history"
        params = {"component": project, "metrics": metrics, "ps": "500"}

        response = requests.get(analysis_url, params=params, headers=headers)
        analysis_data = response.json()

        for metric in analysis_data.get("measures", []):
            for history in metric.get("history", []):
                writer.writerow([project, history["date"], metric["metric"], history.get("value", "N/A")])

print(f"Analysis data saved to {csv_file}")
