# Simple-Interpreter
I built an interpreter, which given a booelan formula it will print the corresponding truth table.

## Tokenization
1. **Comments**: everything after '#' is ignored.
2. **Special characters**: There are 4 special characters: “(”, “)”, “=” and “;”.
3. **Words**: a word is any sequence of (one or more) consecutive letters (“A”, ..., “Z” and “a”, ..., “z”), digits (“0”, ..., “9”) and underscores (“ ”) that starts with a letter or an underscore.
4. **Blanks**: Spaces (“ ”), tabs (“\t”), carriage returns (“\r”) and newlines (“\n”) are consideredblank characters. All blank characters are ignored except for the fact that they can separate two words.
5. **Keywords and identifiers**: There are 8 keywords: “var”, “show”, “show", “or”, “True”, “False”. Any other word is an identifier.

## Parsing

We define here how a program is to be parsed, once it has been tokenized into a sequence of keywords, identifiers, and special characters. A program is a sequence of instructions, each of which is either:  
(a) a declaration,  
(b) an assignment, or  
(c) a “show” instruction.

### (a) Variable Declaration:
1. The keyword `var`, followed by  
2. A sequence of identifiers, then  
3. A semicolon (`;`).  

Identifiers cannot have been previously declared (neither as a variable nor by an assignment).

### (b) Assignment:
1. An identifier, followed by  
2. The special character `=`, and  
3. An expression, then  
4. A semicolon (`;`).  

The identifier in step (1) cannot have been previously declared (neither as a variable nor by an assignment). Before the assignment, every identifier present in the expression must have been either declared as a variable or defined by an earlier assignment. In particular, the identifier in step (1) cannot be used in the expression.

### (c) "Show" Instruction:
1. The keyword `show` or `show_ones`, followed by  
2. A list of identifiers, then  
3. A semicolon (`;`).  

Each identifier must have been defined by a prior assignment.

---

### Expressions in Assignments
The expression in step (b.iii) is a Boolean formula involving elements. An element can be:  
- The keyword `True`,  
- The keyword `False`, or  
- Any identifier that was defined previously (either by a variable declaration or by an assignment).  

An expression is either:  
1. An element,  
2. The negation (`not`) of a sub-expression,  
3. A conjunction (`and`) of two or more sub-expressions, or  
4. A disjunction (`or`) of two or more sub-expressions.  

If those sub-expressions are not elements themselves, they must be surrounded by parentheses. As a result, there is no need for operator priorities.

---

### BNF Grammar

```bnf
<element> ::= "True" | "False" | <identifier>
<paren-expr> ::= <element> | "(" <expr> ")"
<negation> ::= "not" <paren-expr>
<conjunction> ::= <paren-expr> "and" <paren-expr> | <paren-expr> "and" <conjunction>
<disjunction> ::= <paren-expr> "or" <paren-expr> | <paren-expr> "or" <disjunction>
<expr> ::= <negation> | <conjunction> | <disjunction> | <paren-expr>
<id-list> ::= <identifier> | <identifier> <id-list>
<instruction> ::= "var" <id-list> ";" 
                | <identifier> "=" <expr> ";" 
                | "show" <id-list> ";" 
                | "show_ones" <id-list> ";"
<program> ::= <instruction> | <instruction> <program>
