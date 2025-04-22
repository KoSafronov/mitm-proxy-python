def scan_request(request_data):
    url = request_data.get("url", "")
    report = []

    if "<script>" in url.lower():
        report.append("Possible XSS")

    if "' or 1=1" in url.lower():
        report.append("Possible SQL Injection")

    return report or ["No issues found"]
