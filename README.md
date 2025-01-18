# README.md
# Feature Flag Parser Action

Parse Swift feature flags and update a central repository.

## Usage

1. Create a repository to store flags
2. Create a Personal Access Token with repo access
3. Add token as secret `FLAGS_REPO_TOKEN` to your repository
4. Add workflow:

```yaml
name: Update Flags
on:
  push:
    paths: ['**/*FeatureFlag.swift']
jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: username/tiny-flagging-action@v1
        with:
          flags_repo: 'org/flags-repo'
          token: ${{ secrets.FLAGS_REPO_TOKEN }}
```

## Feature Flag Format

```swift
// String flags
enum AppStringFeatureFlag {
    case welcomeMessage
    case apiEndpoint
    
    var defaultValue: String {
        switch self {
        case .welcomeMessage: return "Welcome!"
        case .apiEndpoint: return "https://api.example.com"
        }
    }
}

// Boolean flags
enum AppBoolFeatureFlag {
    case enableSearch
    case enableFilters
    
    var defaultValue: Bool {
        switch self {
        case .enableSearch: return true
        case .enableFilters: return false
        }
    }
}
```