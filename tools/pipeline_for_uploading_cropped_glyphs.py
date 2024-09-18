import os
import shutil
from pathlib import Path
import git
from github import Github

token = os.environ.get("GITHUB_TOKEN")

def create_github_repo(repo_name):
    github_client = Github(token)
    org = github_client.get_organization("MonlamAI")
    try:
        repo = org.create_repo(repo_name, private=False)
        print(f"Created GitHub repository: {repo_name}")
    except Exception as e:
        print(f"Failed to create GitHub repository {repo_name}: {e}")
        return None
    return repo

def publish_repo(local_repo, dir_names):
    repo_name = local_repo.name
    if not create_github_repo(repo_name):
        return

    repo = git.Repo.init(local_repo)

    if not repo.head.is_valid():
        repo.index.add(repo.untracked_files)
        repo.index.commit("initial commit")

    if 'origin' not in repo.remotes:
        origin = repo.create_remote(
            'origin', f'https://{token}:x-oauth-basic@github.com/MonlamAI/{repo_name}.git')
    else:
        origin = repo.remote('origin')

    try:
        origin.push(refspec='HEAD:refs/heads/main', force=True)
        print(f"Published repo: {repo_name}")
    except git.exc.GitCommandError as e:
        print(f"Failed to push repository {repo_name}: {e}")

    
    found_glyph_list = local_repo / "all_glyphs_F9.txt"
    with open(found_glyph_list, "w", encoding="utf-8") as f:
        for name in dir_names:
            f.write(f"{name}\n")

def create_repo_folders(parent_dir, glyph_dirs, font_num):
    glyph_names = []
    repo_dirs = []
    repo_name = f"F{font_num:04}"
    current_repo_dir = parent_dir / repo_name
    current_repo_dir.mkdir(parents=True, exist_ok=True)

    all_dir_names = []

    for glyph_dir in glyph_dirs:
        if glyph_dir.is_dir() and len(list(glyph_dir.iterdir())) >= 1:
            if len(repo_dirs) == 10:
                repo_dirs = []
                font_num += 1
                repo_name = f"F{font_num:04}"
                current_repo_dir = parent_dir / repo_name
                current_repo_dir.mkdir(parents=True, exist_ok=True)
                all_dir_names.clear()

            repo_dirs.append(glyph_dir)
            dest_dir = current_repo_dir / glyph_dir.name
            if not dest_dir.exists():
                shutil.copytree(glyph_dir, dest_dir)
                glyph_names.append(glyph_dir.name)
                all_dir_names.append(glyph_dir.name)
                print(f"Copied {glyph_dir} to {dest_dir}")
            else:
                print(f"Destination {dest_dir} already exists, skipping.")

    return glyph_names, all_dir_names

def create_repo_for_glyph(font_num):
    glyph_dirs = list(Path("data/glyphs/kumbum").iterdir())
    parent_dir = Path("data/batched_glyphs/kumbum")
    parent_dir.mkdir(parents=True, exist_ok=True)
    glyph_names, all_dir_names = create_repo_folders(parent_dir, glyph_dirs, font_num)
    for repo_dir in parent_dir.iterdir():
        if repo_dir.is_dir():
            publish_repo(repo_dir, all_dir_names)

def main():
    font_num = 90000
    create_repo_for_glyph(font_num)

if __name__ == "__main__":
    main()
