
import Foundation

enum AppStringFeatureFlag: String {
    case welcomeMessage
    case apiEndpoint
    case searchName
    
    var defaultValue: String {
        switch self {
        case .welcomeMessage: 
            return "Welcome to the app ❤️"
        case .apiEndpoint:
            return "https://api.default.com"
        case .searchName:
            return "Type in header..."
        }
    }
}