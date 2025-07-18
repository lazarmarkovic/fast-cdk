from importlib.resources import files

# from jinja2 import StrictUndefined, Template
from textx import metamodel_from_str

# grammar_path = files("fastcdk.grammars") / "meta_template_grammar.tx"
grammar_path = files("fastcdk.grammars") / "fcdk_def_grammar.tx"
grammar_text = grammar_path.read_text()

# print(f"Using grammar from: {grammar_path}")
# print(f"Grammar text:\n{grammar_text}\n")

# template_path = files("fastcdk.stack_template.lib.modules.cloudwatch_log") / "log.meta_template"
dsl_path = files("fastcdk.fastcdk_dsl_examples") / "network_example.fcdk"
dsl_text = dsl_path.read_text()

# print(f"Using template from: {template_path}")
# print(f"Template text:\n{template_text}\n")

fastcdk_mm = metamodel_from_str(grammar_text, skipws=True)

# template = template_text

# j2_template = Template(template_text, undefined=StrictUndefined)

# data = {}
# for statement in program.statements:
#   data[statement.var] = statement.value

# print(j2_template.render(data))


program = fastcdk_mm.model_from_str(dsl_text)

# for statement in program.default_inputs_section.inputs:
#   print(f"Input: {statement.key} = {statement.val}")

# print(program.__dict__.keys())
