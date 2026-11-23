"""Publish the website: push `main` to GitHub.

GitHub Actions (.github/workflows/deploy.yml) then uploads the site/ folder by FTP into
theartfulproducts.com's own folder on MilesWeb. Only changes inside site/ trigger an upload.

Run from the project folder after committing:   python tools/publish.py
Add --dry-run to check without pushing."""
import subprocess, sys

def git(*args, capture=True):
    r = subprocess.run(["git", *args], capture_output=capture, text=True)
    if r.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stderr or r.stdout}")
    return (r.stdout or "").strip()

dry = "--dry-run" in sys.argv
if git("rev-parse", "--abbrev-ref", "HEAD") != "main":
    sys.exit("Switch to the main branch first (git checkout main).")
if git("status", "--porcelain"):
    sys.exit("You have uncommitted changes. Commit them first, then publish.")

files = git("ls-tree", "-r", "--name-only", "HEAD", "site").splitlines()
leaks = [f for f in files if f.endswith(("artful-config.php", ".sqlite", ".pdf")) or "/_incoming/" in f]
if "site/index.html" not in files or leaks:
    sys.exit(f"Refusing to publish: site/index.html present: {'site/index.html' in files}; private files in site/: {leaks}")

ahead = git("rev-list", "--count", "origin/main..main") if git("ls-remote", "--heads", "origin", "main") else "?"
print(f"main -> {git('rev-parse', '--short', 'main')}  ({len(files)} website files, {ahead} new commit(s))")
if dry:
    sys.exit("Dry run: nothing pushed.")
# the Instagram job commits social/posted.json on GitHub, so bring those commits in first
git("pull", "--rebase", "--quiet", "origin", "main", capture=False)
git("push", "origin", "main", capture=False)
print("Pushed. GitHub Actions uploads site/ to theartfulproducts.com: watch it under the repo's Actions tab.")
