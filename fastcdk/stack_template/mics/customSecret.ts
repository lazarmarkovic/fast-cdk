// External imports
import * as iam from "aws-cdk-lib/aws-iam";
import * as secretmng from "aws-cdk-lib/aws-secretsmanager";

export abstract class CustomSecret {
  public secret: secretmng.ISecret;

  constructor() {
  }

  public giveAccessPermissionToRole(role: iam.Role) {
    this.secret.addToResourcePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      principals: [new iam.ArnPrincipal(role.roleArn)],
      actions: ["secretsmanager:GetSecretValue"],
      resources: [this.secret.secretArn]
    }));
  }

}