import * as fs from "fs";
import * as path from "path";
import * as TOML from "@iarna/toml";
import { configValidationSchema, EnvConfig } from "./configSchema";

export function loadConfig(environment: string): EnvConfig {
  const configPath = path.join(process.cwd(), "env-config", `${environment}.toml`);
  try {
    // Check if file exists
    if (!fs.existsSync(configPath)) {
      throw new Error(`Configuration file not found: ${configPath}`);
    }

    // Read and parse TOML file
    const configContent = fs.readFileSync(configPath, "utf-8");
    const config = TOML.parse(configContent);

    // Validate configuration
    const { error, value } = configValidationSchema.validate(config, {
      abortEarly: false,
      allowUnknown: false,
    });

    if (error) {
      throw new Error(`Configuration validation failed: ${error.message}`);
    }

    return value as EnvConfig;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to load configuration: ${error.message}`);
    }
    throw error;
  }
}