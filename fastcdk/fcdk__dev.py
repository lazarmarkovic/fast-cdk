from importlib.resources import files

from fastcdk.fcdk import Fcdk

dsl_path = files("fastcdk.fastcdk_dsl_examples") / "network_example.fcdk"

fcdk_loaded = Fcdk(dsl_path)


