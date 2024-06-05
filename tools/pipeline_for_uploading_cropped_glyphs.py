import os
import shutil
from pathlib import Path
import git
from github import Github

def create_github_repo(repo_name):
    token = os.environ.get("GITHUB_TOKEN")
    github_client = Github(token)
    org = github_client.get_organization("MonlamAI")
    try:
        repo = org.create_repo(repo_name, private=False)
        print(f"Created GitHub repository: {repo_name}")
    except Exception as e:
        print(f"Failed to create GitHub repository {repo_name}: {e}")
        return None
    return repo

def publish_repo(local_repo):
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = local_repo.name
    if not create_github_repo(repo_name):
        return

    repo = git.Repo.init(local_repo)

    if not repo.head.is_valid():
        repo.index.add(repo.untracked_files)
        repo.index.commit("initial commit")

    if 'origin' not in repo.remotes:
        origin = repo.create_remote(
            'origin', f'https://{token}:x-oauth-basic@github.com/MonlamAI/{local_repo.name}.git')
    else:
        origin = repo.remote('origin')

    try:
        origin.push(refspec='HEAD:refs/heads/main', force=True)
        print(f"Published repo: {local_repo.name}")
    except git.exc.GitCommandError as e:
        print(f"Failed to push repository {local_repo.name}: {e}")

def create_repo_folders(parent_dir, glyph_dirs, filename, num):
    glyph_names = []
    glyph_dir_name = []
    repo_name = f"F{num:04}"
    for glyph_dir in glyph_dirs:
        if len(glyph_dir_name) == 10:
            glyph_dir_name = []
            num += 1
            repo_name = f"F{num:04}"
        if len(list(glyph_dir.iterdir())) == 100:
            glyph_dir_name.append(glyph_dir)
            dest_folder = parent_dir / repo_name
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_dir = dest_folder / glyph_dir.name
            if not dest_dir.exists():
                shutil.copytree(glyph_dir, dest_dir)
                glyph_names.append(glyph_dir.name)
                print(f"Copied {glyph_dir} to {dest_dir}")
            else:
                print(f"Destination {dest_dir} already exists, skipping.")
    Path(parent_dir / filename).write_text("\n".join(glyph_names), encoding='utf-8')

def create_repo_for_glyph(file_name, num):
    glyph_dirs = list(Path("../data/glyphs/shul").iterdir())
    parent_dir = Path("../data/batched_glyphs/")
    parent_dir.mkdir(parents=True, exist_ok=True)
    create_repo_folders(parent_dir, glyph_dirs, file_name, num)
    for repo_dir in parent_dir.iterdir():
        if repo_dir.is_dir():
            repo_num = int(repo_dir.name[1:])
            if repo_num >= 20005:
                continue
            publish_repo(repo_dir)

def main():
    num = 20000
    font_name = "F20000"
    file_name = f"{font_name}_glyphs.txt"
    create_repo_for_glyph(file_name, num)

if __name__ == "__main__":
    main()
