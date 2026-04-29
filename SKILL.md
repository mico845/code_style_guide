---
name: code-style-cpp-guide
description: Apply this repository's C++ code style guide when writing, editing, reviewing, refactoring, or explaining C++ code. Use for C++ source/header files and for decisions about headers, include order, namespaces and scope, classes, constructors, copy/move behavior, functions, parameters, return values, C++ language features, macros, and naming conventions.
---

# C++ Code Style Guide

## Workflow

Before writing, changing, or reviewing C++ code, inspect the relevant reference files in `references/`.

Use the guide as the default style authority for:

- Header self-sufficiency, include guards, include dependencies, forward declarations, inline definitions, and include ordering.
- Namespace usage, internal linkage, non-member functions, local variables, and static/global variables.
- Class design, constructors, conversions, copy/move behavior, struct vs class, inheritance, operators, access control, and declaration order.
- Function returns, input/output parameters, short functions, overloads, default arguments, and trailing return types.
- C++ feature choices, type usage, and macro usage.
- File, type, variable, function, namespace, enum, and macro naming.

When multiple rules may apply, prefer the most specific chapter first, then use the broader guidance as context. If existing code conflicts with the guide, preserve local consistency unless the user asks for a style correction or the surrounding change is already touching that pattern.

## References

- `references/0.introduction.md` - introduction.
- `references/1.headers.md` - headers.
- `references/2.scope.md` - scope.
- `references/3.classes.md` - classes.
- `references/4.functions.md` - functions.
- `references/5.cpp-features.md` - cpp features.
- `references/6.naming-conventions.md` - naming conventions.
