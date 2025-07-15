#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { StackRoot } from "../lib/stack.root";
import { loadConfig } from "../config/configLoader";

const app = new cdk.App();
const environmentName = app.node.tryGetContext("env");

// Initialize config
const envConfig = loadConfig(environmentName);

// Init stack
new StackRoot(app, `${envConfig.AwsStackName}${envConfig.Environment}`, envConfig);

// Add tags
cdk.Tags.of(app).add("Project", envConfig.Project);
cdk.Tags.of(app).add("Environment", envConfig.Environment);
cdk.Tags.of(app).add("Version", envConfig.Version);
