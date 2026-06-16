# Repository Rename Plan

This PR does not rename the GitHub repository or the local folder.

## Future GitHub Rename

When maintainers are ready, rename the GitHub repository to:

```text
techtools-for-windows
```

Do not reuse the old `taskbar-listview` repository name for a different
project. Leaving the old name unused avoids confusing redirects, stale links,
and accidental issue or pull request routing.

## Future Local Remote Update

After the GitHub repository is renamed, existing local clones can update their
remote URL, for example:

```powershell
git remote set-url origin https://github.com/<owner>/techtools-for-windows.git
git remote -v
```

Replace `<owner>` with the real repository owner at the time of the rename.

## Local Folder

The local folder may be renamed later if maintainers want the filesystem path
to match the repository slug. That is intentionally out of scope for this PR.
