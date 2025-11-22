# Fast CDK Domain Specific Language

<p align="center">
  <img src="images/icon.png" alt="FastCDK logo" width="160" />
</p>

### FastCDK is extensible Domain Specific Language for generating Typescript-based AWS infrastructure-as-code projects using AWS CDK library system.

### System consists of two parts: 
1. Definitions of CDK constructs and their templates (.fcdk_def and .j2 files)
2. Stack Instance files (.fcdk files)

#### FastCDK:

1. Takes default FastCDK Definitions (by default defined in ./stack_template/lib/modules/*) and even custom/extended ones from given directories (here present at ./fcdk_def_examples/*) and builds semantic dependancy graph of those definitions.
2. Then it loads given FastCDK Instance specification file(s) (examples present in ./fcdk_examples/*) where definitions can be:
    - instantiated
    - their attributes configured
    - their attributes inheritted
    - their dependancies overridden
Compilation consists of graph traversal to find subgraph of dependant definitions which is then transformed into a list of contexts which are used with Jinja2 to generate Typescript files in form of consistent AWS CDK Project.

### CLI Arguments & Flags

| Name               | Type                     | Description                                                         |
|--------------------|---------------------------|---------------------------------------------------------------------|
| `INSTANCE_FILES...` | argument (repeatable)     | One or more `.fcdk` instance files to compile.                      |
| `--defs-dir DIR`   | option (repeatable)       | Directory containing custom `.fcdk_def` and `.j2` definition files. |
| `--out PATH`       | option                    | Output folder for the generated CDK project. Default: `./generated`.|
| `--make-graph`     | flag                      | Generates an HTML dependency graph (`graph_viz.html`).              |
| `--dry-run`        | flag                      | Prints parsed arguments as JSON and exits without generating code.  |
| `--debug`          | flag                      | Enable exception traces                                             |


### Steps to test:
- Install: ```pip install -e .```
- Show Flag Help: ```fastcdk --help```
- Generate CDK project in default folder ```(./generated)``` with default defs:
```
fastcdk ./fcdk_examples/the_one_with_all_stuff.fcdk 
fastcdk ./fcdk_examples/the_one_with_much_inheritance.fcdk
fastcdk ./fcdk_examples/the_one_with_networks.fcdk
fastcdk ./fcdk_examples/the_one_with_big_frontend.fcdk
```

- Generate to specific folder ```(--out ./my-cdk-proj)``` with custom/extended defs ```(stored in 'fcdk_def_examples')```:
```
fastcdk ./fcdk_examples/the_one_with_extended_defs.fcdk \
        --defs-dir ./fcdk_def_examples \
        --out ./my-cdk-proj
```

- Generate definition dependancy graph ```(with flag --make-graph)``` with instance stack as root ```(generated as HTML file ./graph_viz.html)```:
```
fastcdk ./fcdk_examples/the_one_with_big_frontend.fcdk \
        --out ./my-cdk-proj \
        --make-graph
```

#### Code merge of generated code with custom code is solved by using predefined protected regions in template files, those parts are marked by start and end comment:
```
// fastcdk:keep-start id=S3cfFrontend.ExtraPolicy sig=v0.0.1>
// fastcdk:keep-end
```

```id``` identifies protected region when rendered file is parsed to extract code from protected region
```sig``` represents protected region version defined in j2 tempalte, 

If the sig version in tempalte and in generated tempalte are the same, code in protected regions will always be kept intact after each new generation.
But if developer bumps version (v0.0.1 -> v0.0.2) in template and then user regenerated following code:
```
    // fastcdk:keep-start id=Network.ExtraTags sig=v0.0.1
    console.log("something else ")
    
    console.log("something else 2")
    // fastcdk:keep-end
```
he will get:
```

    // fastcdk:keep-start id=Network.ExtraTags sig=v0.0.2
/* >>> fastcdk:CONFLICT (signature changed)
old user code:
--------------------------------

    console.log("something else ")
    
    console.log("something else 2")
--------------------------------
update this region to the new template context (version bumped)
*/
    // fastcdk:keep-end
```
This will indicate that code in protected region might need to be refactored becuase template code above has been updated (marked by bumping of region's version in tempalte). User can delete conflict markers and keep the code or change it, the code will stay the same after each generation.



## VS Code Extension
Code for custom VS Code extension is lcoated in ```fast-cdk-vscode``` folder. Steps to install build and install it:

- Install deps: `npm install`
- Build: `npm run build`
- Package (maey need to install tool `vsce`): `vsce package`
- Install: `code --install-extension fast-cdk-vscode-0.1.0.vsix`

This extension will also install it's dependancy extension [TextX](https://marketplace.visualstudio.com/items?itemName=textX.textX).

After FastCDK extension is installed, install the textX project to enable Language Server support as shown on textX extension page [TextX](https://marketplace.visualstudio.com/items?itemName=textX.textX).


## License

MIT License © 2025 Lazar M. Marković