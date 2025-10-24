# Fast CDK

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

### Steps to test:
- Install: ```pip install -e .```
- Show Flag Help: ```fastcdk --help```
- Generate CDK project in default folder ```(./generated)``` with default defs:
```
fastcdk ./fcdk_examples/the_one_with_all_stuff.fcdk 
fastcdk ./fcdk_examples/the_one_with_much_inheritance.fcdk
fastcdk ./fcdk_examples/the_one_with_networks.fcdk
fastcdk ./fcdk_examples/the_one_with_big_prontend.fcdk
```

- Generate to specific folder ```(--out ./my-cdk-proj)``` with custom/extended defs ```(stored in 'fcdk_def_examples')```:
```
fastcdk ./fcdk_examples/the_one_with_extended_defs.fcdk \
        --defs-dir ./fcdk_def_examples \
        --out ./my-cdk-proj
```

- Generate definition dependancy graph ```(with flag --make-graph)``` with instance stack as root ```(generated as HTML file ./graph_viz.html)```:
```
fastcdk ./fcdk_examples/the_one_with_big_prontend.fcdk \
        --out ./my-cdk-proj \
        --make-graph
```
