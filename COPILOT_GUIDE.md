# GitHub Copilot Guide

## Prerequisites
- GitHub CLI (`gh`) is already installed ✓
- You are already logged in ✓

## Using GitHub Copilot with gh CLI

### 1. Install GitHub Copilot

First, you need to install the GitHub Copilot extension for the GitHub CLI:

```bash
gh extension install github/gh-copilot
```

### 2. Using GitHub Copilot

After installation, you can use GitHub Copilot directly from the command line:

#### Get code suggestions
```bash
gh copilot suggest "how to create a Python function to sort a list?"
```

#### Get command explanations
```bash
gh copilot explain "git rebase -i HEAD~3"
```

### 3. Common Use Cases

#### Get shell command suggestions
```bash
gh copilot suggest -t shell "find all files larger than 100MB"
```

#### Get git command suggestions
```bash
gh copilot suggest -t git "undo last commit"
```

#### Get GitHub CLI command suggestions
```bash
gh copilot suggest -t gh "list all open pull requests"
```

### 4. Interactive Mode

You can also use GitHub Copilot in interactive mode:

```bash
gh copilot
```

This opens an interactive session where you can chat directly with Copilot.

### 5. Useful Tips

- **Ask precise questions**: The more specific your question, the better the answer
- **Provide context**: Include relevant details about your problem
- **Try different commands**: Use `suggest` for suggestions and `explain` for explanations

### 6. More Information

For additional help, use:
```bash
gh copilot --help
```

Or visit the official documentation: https://docs.github.com/en/copilot/github-copilot-in-the-cli

## GitHub Copilot in Your IDE

If you want to use GitHub Copilot in your development environment (such as VS Code, IntelliJ, etc.):

1. Install the appropriate Copilot extension from the Extension Marketplace
2. Sign in with your GitHub account
3. Copilot will automatically make code suggestions as you type

### VS Code
```bash
# Install VS Code Copilot Extension
code --install-extension GitHub.copilot
```

## Troubleshooting

If you encounter issues:

```bash
# Check status
gh auth status

# Re-authenticate if necessary
gh auth login

# Update extension
gh extension upgrade gh-copilot
```

## Summary

You can now use GitHub Copilot with these simple commands:
- `gh copilot suggest` - For suggestions
- `gh copilot explain` - For explanations
- `gh copilot` - For interactive mode

Good luck with GitHub Copilot! 🚀
