# Commit Message Structure

commit message format SHOULD consist of a header, body and footer.

```
<header>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

1. The header is mandatory and should be concise: the `<short summary>` should be within about 20–30 Traditional Chinese characters (roughly 50 display columns for the whole header). It MUST be in the format of `<type>: <short summary>`, where:

- `<type>` is the commit type, MUST be one of the types defined in the [commit type](commit-types.md) document. Please refer to the document to check meaning of each type.

- `<short summary>` is a succinct description of the change.
    - Do not end the summary with a period (。 or .).
    - English grammar rules (imperative tense, capitalization) do not apply, since the summary is written in Traditional Chinese.

2. The body is optional and should provide a more detailed description of the change.
   Explain the motivation for the change in the commit message body. This commit message should explain why you are making the change. You can include a comparison of the previous behavior with the new behavior in order to illustrate the impact of the change.

3. The footer is optional and should include any relevant information about breaking changes or issues closed by the commit. The keywords (`BREAKING CHANGE:`, `DEPRECATED:`, `Fixes #`, `Closes #`) MUST stay in English so tools can parse them; the descriptions are written in Traditional Chinese. For example:

```
BREAKING CHANGE: <breaking change summary>
<BLANK LINE>
<breaking change description + migration instructions>
<BLANK LINE>
<BLANK LINE>
Fixes #<issue number>
```

or

```
DEPRECATED: <what is deprecated>
<BLANK LINE>
<deprecation description + recommended update path>
<BLANK LINE>
<BLANK LINE>
Closes #<pr number>
```

4. For a `revert` commit, the header is `revert: <header of the reverted commit>`, and the body MUST contain `還原 commit <SHA>` followed by the reason for the revert.
