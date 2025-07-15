from jinja2 import StrictUndefined, Template
from textx.metamodel import metamodel_from_str

from fastcdk.meta_model.meta_template_grammar import MM
from fastcdk.templates.vpc_jinja import VPC_TEMPALTE

# from fastcdk.templates.vpc_jinja import VPC_TEMPALTE

fastcdk_mm = metamodel_from_str(MM)

program = fastcdk_mm.model_from_str(
  """
    VPC NATGatewayCount = 3
  """
)

template = VPC_TEMPALTE

j2_template = Template(template, undefined=StrictUndefined)

data = {}
for statement in program.statements:
  data[statement.var] = statement.value

print(j2_template.render(data))
