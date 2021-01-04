# The MMD format

This project aims to be a simple lightweight alternative to Latex when writing
mathematics.


## File format

Every Markdown file (as defined [here](https://daringfireball.net/projects/markdown/syntax))
is valid MMD.
The only addition in parsing is that one may annotate blockquotes in order to 
produce theorems, lemmas, proofs, etc. in the following way
```
<DIRECTIVE>[<identifier>] <name>
>
> .......
>
```

Explanation:
  - `<DIRECTIVE>`: This must be in uppercase and letters only and describes the 
    type, e.g. THEOREM, LEMMA, PROOF, ...
  - `<identifier>`: Must consist of lowercase letters, numbers and dashes. Used
    to identify statements and alike uniquely.
  - `<name>`: Free displayed text to describe the piece: 
    e.g. "Fundamental theorem of Algebra", "Schur-Zassenhaus",...

## Parser
