import time # Idhai mela import line-la add pannikonga

# 🔥 APPLE WAF BYPASS SHIELD 🔥
def fetch_json(url, params=None):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.15',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1'
    ]
    
    # Apple cache/firewall ematha oru random timestamp add pandrom
    if params is not None:
        params['nocache'] = int(time.time() * 1000)
        # India server block aana, US server-kku maathi vidu
        if params.get('country') == 'IN':
            params['country'] = random.choice(['IN', 'US', 'GB']) 

    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://music.apple.com/'
    }
    
    try:
        res = requests.get(url, params=params, headers=headers, timeout=15)
        
        # HTML error page vandhalum thooki poduradhukku check pandrom
        if res.status_code == 200 and 'newNullResponse' not in res.text:
            return res.json()
        else:
            print(f"⚠️ [API Blocked] Switching region or use VPN...")
            return None
    except Exception:
        return None
