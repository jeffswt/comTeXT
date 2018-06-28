
class LanguageSupport:
    """Multiple language indexer."""

    all_strings = {
        "en-US": {
            "Parser.Error.Header.Unterminated":
                "expected front matter's end marker",
            "Parser.Error.Header.ParseError":
                "failed to parse yaml front matter, reason:\n%s",
            "Parser.Error.Scope.ExpectedBeginMarker":
                "expected '%s' before scope",
            "Parser.Error.Scope.ExpectedEndMarker":
                "expected '%s' at end of input",
            "Parser.Error.Scope.UnexpectedBeginMarker":
                "unexpected '%s' opening",
            "Parser.Error.Scope.UnexpectedEndMarker":
                "unexpected '%s' closing",
            "Parser.Error.Scope.Outdented":
                "outdented scope, expected indentation > %d",
            "Parser.Error.Function.UnknownFunction":
                "no suitable function found",
            "Parser.Error.Function.ExpectedLineBreak":
                "expected immediate line break after command",
            "Parser.Error.Function.MissingDefMarker":
                "expected ':' in function definition",
            "Parser.Error.Function.TooManyDefMarkers":
                "unexpected ':' after function name",
            "Parser.Error.Function.ConflictLanguage":
                "conflicting language definition",
            "Parser.Error.Function.ConflictMode":
                "conflicting function type",
            "Parser.Error.Function.ConflictBreak":
                "conflicting autobreak mode",
            "Parser.Error.Function.ForbidChar":
                "forbidden character in argument",
            "Parser.Error.Function.UnknownParam":
                "unknown parameter",
            "Parser.Error.Function.ConflictCode":
                "redefinition of the same function",
            "Parser.Error.Function.ParamMismatch":
                "parameters differ between function definitions",
            "Parser.Error.Environment.UnknownEnvironment":
                "no suitable environment found",
            "Parser.Error.Environment.TooFewArgs":
                "too few arguments taken",
            "Parser.Error.Environment.LastMustVerbatim":
                "the last argument must be verbatim",
            "Parser.Error.Environment.ExpectedLineBreak":
                "expected line break",
            "Parser.Error.Library.FileNotFound":
                "described library does not exist",
        },
        "zh-CN": {
        },
        "ja-JP": {
        },
    }

    def __init__(self, lang='en-US'):
        if lang not in LanguageSupport.all_strings:
            lang = 'en-US'
        self.strings = LanguageSupport.all_strings[lang]
        return

    def get_text(self, index):
        if index not in self.strings:
            return index
        return self.strings[index]
    pass


language_support = LanguageSupport('en-US')


def text(index):
    return language_support.get_text(index)
