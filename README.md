# Gemini AI Code Review Action

A GitHub Action that automatically performs code reviews on pull requests using Gemini AI. The action analyzes code changes and provides feedback as a comment on the pull request.

## Features

- Automated code review on pull requests
- Customizable review prompts, max output tokens, etc.
- Support for including context from additional files
- Configurable context lines for better diff understanding
- Error handling with optional error reporting

## Usage

Add the following workflow to your repository at `.github/workflows/code-review.yml`:

```yaml
name: Code Review

on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: sshnaidm/gemini-code-review-action@v1
        with:
          gemini-key: ${{ secrets.GEMINI_API_KEY }}
```

## Prerequisites

1. Gemini API key
   - Add the API key to your GitHub repository secrets as `GEMINI_API_KEY`

## Configuration Options

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `gemini-key` | Gemini API key | Yes | - |
| `github-token` | GitHub token for API authentication | No | `${{ github.token }}` |
| `prompt` | Custom prompt for the AI review | No | Default review prompt |
| `model` | The Gemini language model to use for code review | No | `gemini-2.5-flash` |
| `thinking` | The thinking mode for Gemini. Can be `dynamic`, `off` or tokens number. | No | - |
| `temperature` | The temperature for Gemini | No | `0.0` |
| `top-p` | The top_p value for Gemini | No | `0.0` |
| `max-output` | Limit the length of the output to a certain number of tokens | No | - |
| `post-if-error` | Post comment even if review fails | No | `true` |
| `context-lines` | Number of context lines in diff | No | `10` |
| `add-files` | Include all changed files in review | No | `false` |
| `review-title` | Title of the review comment | No | `Gemini Code Review` |

## Advanced Usage Examples

### Custom Review Prompt

```yaml
- uses: sshnaidm/gemini-code-review-action@v1
  with:
    gemini-key: ${{ secrets.GEMINI_API_KEY }}
    prompt: |
      Please review this code with focus on:
      - Security issues
      - Performance optimizations
      - Best practices
```

### Include Additional Context

```yaml
- uses: sshnaidm/gemini-code-review-action@v1
  with:
    gemini-key: ${{ secrets.GEMINI_API_KEY }}
    add-files: 'true'
    context-lines: '20'
    review-title: 'Code Review by Gemini AI'
```

## Outputs

The action provides the following outputs:

- `results`: The complete results of the code review

## Error Handling

By default, the action will post a comment even if the review process encounters an error. This behavior can be disabled by setting `post-if-error: 'false'`.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and feature requests, please open an issue in the GitHub repository.
