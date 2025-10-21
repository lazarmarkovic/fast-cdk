from importlib.resources import files

cdk_project_files = [
  files("fastcdk.stack_template.bin") / "main.ts",
  files("fastcdk.stack_template.config") / "configLoader.ts",
  #files("fastcdk.stack_template.config") / "configSchema.ts",
  #files("fastcdk.stack_template.env-config") / "example.toml",
  files("fastcdk.stack_template.misc") / "customSecret.ts",
  files("fastcdk.stack_template.misc") / "deploymentEnvEnum.ts",
  files("fastcdk.stack_template.test") / "std_cdk.test.ts",
  files("fastcdk.stack_template") / ".gitignore",
  files("fastcdk.stack_template") / ".npmignore",
  files("fastcdk.stack_template") / "cdk.json",
  files("fastcdk.stack_template") / "jest.config.js",
  files("fastcdk.stack_template") / "package.json",
  files("fastcdk.stack_template") / "README.md",
  files("fastcdk.stack_template") / "tsconfig.json",
]
