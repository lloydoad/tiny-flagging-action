# README.md
# Feature Flag Parser Action

Parse Swift feature flags and update a central repository.

## Usage

1. Add workflow to your repository
2. Create flags using the required Feature Flag Format
3. Push your changes to github
4. Flags available at https://{{username}}.github.io/{repository name}/

```yaml
name: Sync Feature Flags - TinyFlag
on:
  push:
    paths: ['**/generated_feature_flags/**', '**/*FeatureFlag.swift']
jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      # Required for updating stored flags
      contents: write
    steps:
      # checkout current repo
      - uses: actions/checkout@v3
      # checkout tiny flags repository
      - uses: lloydoad/tiny-flagging-action@main
        with:
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
