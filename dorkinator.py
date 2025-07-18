#!/usr/bin/env python3

import sys
import urllib.parse
from colorama import Fore, Style, init

init(autoreset=True)

DORKS_TEMPLATE = [
    "site:{d}",
    "site:*.{d}",
    "(site:{d} OR site:api.{d} OR site:cdn.{d})",
    "site:{d} (ext:log OR ext:conf OR ext:ini OR ext:env OR ext:bak OR ext:backup OR ext:swp OR ext:old)",
    "site:{d} (ext:js OR ext:php OR ext:asp OR ext:aspx OR ext:jsp)",
    "site:{d} (ext:sql OR ext:db OR ext:sqlite OR ext:csv OR ext:xml)",
    "site:{d} (filetype:pdf OR filetype:xls OR filetype:ppt OR filetype:doc)",
    "(site:pastebin.com OR site:github.com) \"{d}\"",
    "site:{d} intext:\"BEGIN RSA PRIVATE KEY\" OR intext:\"PRIVATE KEY-----\"",
    "site:{d} intext:\"AKIA\" OR intext:\"ASIA\" OR intext:\"aws_secret_access_key\"",
    "site:{d} intext:\"xoxp-\" OR intext:\"xoxb-\"",
    "site:{d} intext:\"api_key\" OR intext:\"token=\"",
    "intext:\"client_secret\" site:{d}",
    "site:{d} inurl:/api/ OR inurl:/v1/ OR inurl:/v2/ OR inurl:/graphql",
    "site:{d} inurl:swagger OR inurl:apidocs OR inurl:api-explorer OR inurl:openapi.json",
    "site:{d} inurl:graphql OR filetype:gql OR filetype:graphql",
    "site:{d} intext:\"choose file\" OR inurl:upload OR inurl:file",
    "site:{d} inurl:admin OR inurl:dashboard OR inurl:manage OR intitle:Admin",
    "site:{d} inurl:test OR inurl:dev OR inurl:staging OR inurl:qa OR inurl:sandbox",
    "site:{d} inurl:.git OR inurl:.svn OR inurl:jenkins OR inurl:gitlab OR inurl:bitbucket",
    "site:{d} inurl:?q= OR inurl:?search= OR inurl:?keyword= OR inurl:?lang=",
    "site:{d} inurl:?id= OR inurl:?cat= OR inurl:?action= OR inurl:?page=",
    "site:{d} inurl:?file= OR inurl:?include= OR inurl:?path= OR inurl:?doc=",
    "site:{d} inurl:?exec= OR inurl:?cmd= OR inurl:?run= OR inurl:?do=",
    "site:{d} inurl:?redirect= OR inurl:?url= OR inurl:?next= OR inurl:?return=",
    "site:{d} intitle:\"Error\" OR intitle:\"Exception\" OR intext:\"Stack trace\" OR intext:\"Undefined index\" OR intext:\"SQL syntax\"",
    "site:{d} intext:\"<!--\" intext:\"TODO\" OR intext:\"FIXME\" OR intext:\"DEBUG\"",
    "site:{d} inurl:\"/wp-admin/\" OR inurl:\"/phpmyadmin/\" OR inurl:\"/xampp/\" OR inurl:\"/adminer.php\"",
    "site:s3.amazonaws.com \"{d}\"",
    "site:blob.core.windows.net \"{d}\"",
    "site:storage.googleapis.com \"{d}\"",
    "site:sharepoint.com \"{d}\"",
    "site:onedrive.live.com \"{d}\"",
    "site:dropbox.com/s \"{d}\"",
    "site:box.com/s \"{d}\"",
    "site:{d} (filetype:doc OR filetype:docx OR filetype:xlsx OR filetype:pptx OR filetype:pdf) intext:\"confidential\" OR intext:\"internal use only\" OR intext:\"do not distribute\"",
    "site:openbugbounty.org inurl:reports intext:\"{d}\""
]


def process_domain(domain, engine):
    print(f"\n===============================")
    print(f" 🔎 Generating {engine.capitalize()} Search Links for: {domain}")
    print(f"===============================")

    search_links = []

    for template in DORKS_TEMPLATE:
        dork = template.format(d=domain)
        encoded_dork = urllib.parse.quote(dork)
        if engine == "bing":
            search_url = f"https://www.bing.com/search?q={encoded_dork}"
        else:
            search_url = f"https://www.google.com/search?q={encoded_dork}"
        print(f"\n🔍 {dork}")
        print(f"🌐 {Fore.RED}{search_url}")
        search_links.append(search_url)

    filename = f"{domain}_dorks.txt"
    with open(filename, "w") as f:
        for link in search_links:
            f.write(link + "\n")
    print(f"\n{Fore.GREEN}📁 Saved {len(search_links)} {engine.capitalize()} Search links to: {filename}")


if __name__ == "__main__":
    print(Fore.YELLOW + "\n⚠️  NOTE: Results may be incomplete or inaccurate.")
    print(Fore.YELLOW + "⚠️  Always open the Search links to confirm the findings yourself.\n")

    # Ask for search engine
    engine = ""
    while engine not in ["bing", "google"]:
        engine = input(Fore.CYAN + "💬 Which search engine do you want to use? (bing/google): ").strip().lower()
    print(f"\n✅ You chose: {Fore.GREEN}{engine.capitalize()}\n")

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} [domain | file_with_domains]")
        sys.exit(1)

    arg = sys.argv[1]

    try:
        with open(arg, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        domains = [arg]

    for d in domains:
        process_domain(d, engine)

    print("\n✅ Done.")
    print(f"{Fore.CYAN}🔗 {Style.BRIGHT}My Socials:")
    print(f"{Fore.BLUE}💼 LinkedIn: {Fore.WHITE}https://www.linkedin.com/in/devanshpatelcybersecurity/")
    print(f"{Fore.MAGENTA}✍️  Medium:   {Fore.WHITE}https://medium.com/@devanshpatel930")
    print(f"\n{Fore.GREEN}✨ Stay Curious. Stay Dangerous. ✨\n")
