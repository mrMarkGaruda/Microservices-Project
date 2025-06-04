import requests

MONOLITH_URL = "http://localhost:12101/users/generateWods"
ADMIN_TOKEN = "your_admin_token_here"  # PLACEHOLDER LMFAO

def main():
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    resp = requests.post(MONOLITH_URL, headers=headers)
    print(resp.status_code, resp.json())

if __name__ == "__main__":
    main()