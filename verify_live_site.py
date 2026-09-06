import urllib.request
import json

base_url = 'http://127.0.0.1:5055'

def test_url(url, expected_snippets):
    print(f"Testing {url} ...")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        status = response.status
        content = response.read().decode('utf-8')
        assert status == 200, f"Expected 200, got {status}"
        for s in expected_snippets:
            assert s in content, f"Snippet '{s}' not found in {url}"
        print(f"  [OK] {url} returned 200 and contained all {len(expected_snippets)} expected snippets.")

# 1. Homepage has Accounting link
test_url(f'{base_url}/', [
    'href="computerized-accounting.html"',
    'data-i18n="prog_acc_title">Accounting, Tax and Payroll</a>',
    'class="btn-learn-more"'
])

# 2. Accounting page has all sections and IDs
test_url(f'{base_url}/computerized-accounting.html', [
    'acc_page_title',
    'id="acc-hero-title"',
    'id="acc-hero-badge"',
    'id="acc-stat-1-val"',
    'id="acc-stat-4-val"',
    'id="acc-why-title"',
    'id="acc-cred-title"',
    'id="acc-curriculum-list"',
    'id="acc-admissions-list"',
    'id="acc-faq-list"',
    'id="acc-consultation-form"',
    'QuickBooks Desktop',
    'Sage 50 Accounting',
    'Sage 300 / ACCPAC',
    'Profile &amp; TaxPrep',
    'Advanced Excel'
])

# 3. Route aliases
test_url(f'{base_url}/computerized-accounting', ['acc_page_title'])

# 4. Program API for accounting
print("Testing API /api/programs/accounting ...")
req = urllib.request.Request(f'{base_url}/api/programs/accounting')
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data['success'] is True
    assert data['program']['slug'] == 'accounting'
    assert len(data['program']['detail_json_en']['curriculum_modules']) == 10
    print("  [OK] /api/programs/accounting returned 200 with 10 curriculum modules.")

# 5. Program API alias
print("Testing API /api/programs/computerized-accounting ...")
req = urllib.request.Request(f'{base_url}/api/programs/computerized-accounting')
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    assert data['success'] is True
    assert data['program']['slug'] == 'accounting'
    print("  [OK] /api/programs/computerized-accounting alias resolved successfully.")

print("\nALL LIVE INTEGRATION TESTS PASSED SUCCESSFULLY!")
