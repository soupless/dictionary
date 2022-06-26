# dictionary

A module that allows you to create a dictionary saved as a JSON file.

## What does the dictionary file look like?

A deserialized, typehinted contents of the JSON file is:
```py
{
    "title": str,
    "author": str,
    "description": str,
    "revision_date": str,
    "contents": {
        "<keyword>": {
            "case_sensitive": bool,
            "definitions": list[str],
            "references": list[str]
        },
        ...
    }
}
```

The `<keyword>` could be any string, and here, those are called keywords.

After processing the file, the `Dictionary` class only takes the `contents` and all other keys are properties.

## Usage

As of now, it is useful only if it was used through an interactive shell. This can be done by running `python`, `ipython`, or Jupyter.

To use the dictionary, import `Dictionary` from `dictionary.main`. Note that deleting a key and its value through the `pop` method or using the `del` keyword won't work to avoid data deletion. If one needs to delete the key, use the `remove` method.

However, it is possible to delete the keys of a key of the dictionary, like `del Dictionary(path)['keyword']['references']` as the type of the value of the dictionary keys is `dict` and the deletion methods are not overridden. Please keep this in mind.

## Methods

|Method name|Description|
|---|---|
|`save`|Saves the current copy of the dictionary to the associated file.|
|`definition_of`|Returns the definitions of a keyword from the dictionary, if it exists.|
|`search`|Searches the contents of the current copy of the dictionary for a keyword presented, considering case sensitivity.|
|`add`|Adds content to the dictionary. If the keyword is found, a definition or a reference can be added.|
|`remove`|Removes content from the current copy of the dictionary.|

## Properties

|Property|Description|
|---|---|
|`path`|The path of the file associated.|
|`title`|The title of the dictionary.|
|`author`|The author of the dictionary.|
|`description`|The description of the dictionary.|
|`revision_date`|The date of the last revision of the dictionary.|
|`edited`|An indicator whether the dictionary is edited after it was initialized.|

## License

```
MIT License

Copyright (c) 2022 soupless

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
