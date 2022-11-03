# Introduction

Zen Markup Language is a markup language designed to store application configs. It combines the advantages of JSON, XML and YAML. 

- ZML can store any JSON object.
- ZML keeps high readlibility even with deep nested structure like XML.
- ZML has a XML-like syntax, but is as user-frendly as YAML.
- ZML doesn't rely on indentation like JSON and XML.

# Installation

Just run this command.
```
pip install zen-markup-lang
```

# Quick Start

## Syntax

The syntax of ZML is very intuitive. The follwing example demostrates basic ZML syntax.

```XML
<!zml 0.1>
<a> 114514 </a>
<b> 1919.810 </b>
<c> true </c>
<d> false </d>
<e> null </e>
<f>
    <> "hello`t" </>
    <> "world!" </>
</f>
<g> empty_obj </g>
<h>
    <i> empty_arr </i> 
</h>
```

The ZML file above is equivalent to the following JSON object:

```JSON
{
    "a": 114514,
    "b": 1919.810,
    "c": true,
    "d": false,
    "e": null,
    "f": ["hello\t", "world!"],
    "g": {},
    "h": {
        "i": []
    }
}

```

A major difference is that the escaping character in ZML is \` instead of common \ .

## Use ZML in Python

The package is named `zen_markup_lang`. You can import the package like
```Python
import zen_markup_lang as zml
```

There are four functions in the package, `load`, `loads`, `dump` and `dumps`. They are similar to the functions in Python standard library `json`.

```Python
with open('a.zml') as f:
    d = zml.load(f)
print(zml.dumps(d))
```

That's all. Enjoy! 👏