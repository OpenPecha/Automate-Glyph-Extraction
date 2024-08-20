import time
from pathlib import Path
from git import Repo
from github import Github

org = None


def _get_openpecha_data_org(org_name,token):
    """OpenPecha github org singleton."""
    global org
    if org is None:
        if not org_name:
            org_name = "MonlamAI"
        g = Github(token)
        org = g.get_organization(org_name)
    return org


def get_github_repo(repo_name, org_name, token):
    org = _get_openpecha_data_org(org_name, token)
    repo = org.get_repo(repo_name)
    return repo


def create_github_repo(path, org_name, token, private=False, description=None):
    org = _get_openpecha_data_org(org_name, token)
    repo = org.create_repo(path.stem, description=description, private=private, has_wiki=False, has_projects=False)
    time.sleep(2)
    return repo._html_url.value


def commit(repo_path, message, not_includes, branch="main"):
    if isinstance(repo_path, Repo):
        repo = repo_path
    else:
        repo = Repo(repo_path)
    has_changed = False

    # add untrack fns
    for fn in repo.untracked_files:

        ignored = False
        for not_include_fn in not_includes:
            if not_include_fn in fn:
                ignored = True

        if ignored:
            continue

        if fn:
            repo.git.add(fn)
        if has_changed is False:
            has_changed = True

    # add modified fns
    if repo.is_dirty() is True:
        for fn in repo.git.diff(None, name_only=True).split("\n"):
            if fn:
                repo.git.add(fn)
            if has_changed is False:
                has_changed = True

    if has_changed is True:
        if not message:
            message = "Initial commit"
        repo.git.commit("-m", message)
        repo.git.push("origin", branch)


def create_local_repo(path, remote_url, org, token):
    if (path / ".git").is_dir():
        return Repo(path)
    else:
        repo = Repo.init(path)
        old_url = remote_url.split("//")
        auth_remote_url = f"{old_url[0]}//{org}:{token}@{old_url[1]}"
        repo.create_remote("origin", auth_remote_url)

        repo.config_writer().set_value("user", "name", "ta4tsering").release()
        repo.config_writer().set_value("user", "email", "ta3tsering@gmail.com").release()
        return repo

def github_publish(
    path,
    description,
    message=None,
    not_includes=None,
    org=None,
    token=None,
    private=False,
):
    path = Path(path)
    remote_repo_url = create_github_repo(path, org, token, private,description)
    local_repo = create_local_repo(path, remote_repo_url, org, token)
    commit(local_repo, message, not_includes)