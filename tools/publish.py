"""Publish the website: push `main` (working copy) and update `live` (website only).

MilesWeb's GitHub deploy watches the `live` branch and puts it live on every push, so:
  - `main` = everything (site/, tools/, README, notes)  → never deployed
  - `live` = only the contents of site/, with index.html at the top → deployed to theartfulproducts.com

Run from the project folder after committing:   python tools/publish.py
Add --dry-run to see what would happen without pushing."""
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

sha = git("subtree", "split", "--prefix=site", "main")
files = git("ls-tree", "-r", "--name-only", sha).splitlines()
leaks = [f for f in files if f.lower().startswith(("tools/", "readme", "handover", "_incoming")) or f.endswith(("artful-config.php", ".sqlite", ".pdf"))]
if "index.html" not in files or leaks:
    sys.exit(f"Refusing to publish: live branch would be wrong (index.html present: {'index.html' in files}, private files: {leaks})")

print(f"main  -> {git('rev-parse', '--short', 'main')}")
print(f"live  -> {sha[:7]}  ({len(files)} website files)")
if dry:
    sys.exit("Dry run: nothing pushed.")
git("push", "origin", "main", capture=False)
git("branch", "-f", "live", sha)
git("push", "origin", "live", capture=False)
print("Published. MilesWeb deploys the live branch automatically; check theartfulproducts.com in a minute.")
