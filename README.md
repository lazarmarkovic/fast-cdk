# Fast CDK

Install: pip install -e .

Help:
fastcdk --help

Generate to specific folder with default defs:
fastcdk ./fcdk_examples/all_ex.fcdk \
        --out ./generated


Generate to specific folder with custom extended defs:
fastcdk ./fcdk_examples/the_one_with_extended_defs.fcdk \
        --defs-dir ./fcdk_def_examples
        --out ./generated

fastcdk ./fcdk_examples/the_one_with_extended_defs.fcdk \
        --defs-dir ./fcdk_def_examples/secret_from_resource \
        --out ./generated

fastcdk ./fcdk_examples/the_one_with_extended_defs.fcdk \
        --defs-dir ./fcdk_def_examples \
        --out ./generated