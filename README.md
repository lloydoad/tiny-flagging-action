# README.md
# Feature Flag Parser Action

Parse Swift feature flags and update a central repository.

## Usage

1. Create a repository to store flags
2. Create a Personal Access Token with repo access
3. Add token as secret `FLAGS_REPO_TOKEN` to your repository
4. Add workflow:

```yaml
name: Update Tiny Flags
on:
  push:
    paths: ['**/feature_flags/**', '**/*FeatureFlag.swift']
jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      # checkout current repo
      - uses: actions/checkout@v3
      # checkout tiny flags repository
      - uses: lloydoad/tiny-flagging-action@v2
        with:
          # repository for storing feature flags, defaults to reposity using this workflow
          flags_repo: ${{ github.repository }}
          # token for write access to repository storing feature flags
          token: ${{ secrets.GITHUB_TOKEN }}
```

## Feature Flag Format

```swift
// String flags in AppStringFeatureFlag.swift
enum AppStringFeatureFlag: String {
    case welcomeMessage
    case apiEndpoint
    
    var defaultValue: String {
        switch self {
        case .welcomeMessage: return "Welcome!"
        case .apiEndpoint: return "https://api.example.com"
        }
    }
}

// Boolean flags in AppBoolFeatureFlag.swift
enum AppBoolFeatureFlag: String {
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

## FAQ
### Should each {Bool/String}FeatureFlag enum exist within it's own file? 
Yes

### How do I access the feature flag after it's created?
* Feature flags are accessible through the raw content url of the repository specified in the workflow
* For example, assuming your repository is "username/repo-name", the `.enableSearch` flag will be available at
  "https://raw.githubusercontent.com/username/repo-name/main/feature_flags/SearchBoolFeatureFlag/enableFilters"

### Does `flags_repo` need to be public?
  * No, works out of the box with public repositories.
  * To use a private repo, `secrets.GITHUB_TOKEN` has to be replaced with the relevant token for write access. Requests to the githubusercontent will also need to be authenticated.