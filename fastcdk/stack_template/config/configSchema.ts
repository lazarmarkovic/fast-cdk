import * as Joi from "joi";

export const configValidationSchema = Joi.object({
  AwsStackName: Joi.string().required(),
  AwsAccountId: Joi.string().required().length(12),
  AwsRegion: Joi.string().required(),

  Project: Joi.string().required(),
  Environment: Joi.string().required(),
  Version: Joi.string().required(),
});

export interface EnvConfig {
  AwsStackName: string;
  AwsAccountId: string;
  AwsRegion: string;

  Project: string;
  Environment: string;
  Version: string;
}