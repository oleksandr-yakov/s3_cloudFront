from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions
)
import aws_cdk as cdk
from constructs import Construct
from config import connection_arn, branch


class PipelineStackFront(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_bucket = s3.Bucket(self, "SourceBucket", removal_policy=cdk.RemovalPolicy.DESTROY,                       # delte s3 if stack had been deleted
                                                            bucket_name=f"my-s3-front-{branch}-main-hu4578gf")

        distribution = cloudfront.CloudFrontWebDistribution(self, f"MyDistributionFront-{branch}",
                                                            origin_configs=[cloudfront.SourceConfiguration(
                                                                s3_origin_source=cloudfront.S3OriginConfig(
                                                                    s3_bucket_source=source_bucket),
                                                                behaviors=[
                                                                    cloudfront.Behavior(is_default_behavior=True)], #use this configuration by deffault
                                                            )],
                                                            )

        git_source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            connection_arn=connection_arn,
            owner='fiesta-taco',
            repo='ovsrd-trainee-front',
            branch=branch,   # use global env var : DEV_ENV=dev && cdk deploy <name stack> --profile oyakovenko-trainee
            action_name=f'GitHub_Source_ovsrd-trainee-front-{branch}',
            output=git_source_output,
            trigger_on_push=True,
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name=f'CodeBuildFront-{branch}',
            project=codebuild.PipelineProject(self, f"BuildProjectFront-{branch}",
                                              build_spec=codebuild.BuildSpec.from_object({
                                                  "version": "0.2",
                                                  "phases": {
                                                      "install": {
                                                          # "runtime-versions": {
                                                          #     "nodejs": "14.17.0"
                                                          # },
                                                          "commands": [
                                                              "npm install", #install depnds
                                                          ],
                                                      },
                                                      "build": {
                                                          "commands": [
                                                              "npm run  build",   ##build proj           npm run-script build
                                                          ],
                                                      },
                                                  },
                                                  "artifacts": {
                                                      "files": [
                                                          "dist/**/*",
                                                      ],
                                                  },
                                              }),
                                              ),
            input=git_source_output,
            outputs=[codepipeline.Artifact(artifact_name='output')]
        )

        invalidate_cloudfront_action = codepipeline_actions.CodeBuildAction( #buildspec
            action_name=f"InvalidateCloudFront-{branch}",
            project=codebuild.PipelineProject(
                self, "InvalidateCloudFrontProject",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "phases": {
                        "build": {
                            "commands": [
                                f"aws cloudfront create-invalidation --distribution-id {distribution.distribution_id} --paths '/*'"
                            ],
                        },
                    },
                }),
            ),
            input=git_source_output,
        )

        pipeline = codepipeline.Pipeline(self, f"FrontPipeline-{branch}", stages=[
            codepipeline.StageProps(
                stage_name=f'SourceGit-ovsrd-trainee-front-{branch}',
                actions=[source_action]
            ),
            codepipeline.StageProps(
                stage_name=f'BuildFront-{branch}',
                actions=[build_action]
            ),
            codepipeline.StageProps(
                stage_name=f'DeployFrontS3CloudFront-{branch}',
                actions=[
                    codepipeline_actions.S3DeployAction(
                        action_name='S3Deploy',
                        bucket=source_bucket,
                        input=build_action.action_properties.outputs[0],
                    ),
                    invalidate_cloudfront_action,
                ],
            ),
        ])



