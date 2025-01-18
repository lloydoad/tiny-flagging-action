
import Foundation

enum SearchBoolFeatureFlag: String {
    case enableNewSearch
    case enableFilters
    case enableSuggestions
    case enableHistory

    var defaultValue: Bool {
        switch self {
        case .enableNewSearch, .enableFilters:
            return false
        case .enableSuggestions,
             .enableHistory:
            return true
        }
    }
}