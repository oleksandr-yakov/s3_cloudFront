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


class PipelineStackTestFront(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_bucket = s3.Bucket(self, "SourceBucket", removal_policy=cdk.RemovalPolicy.DESTROY) # delte s3 if stack had been deleted

        distribution = cloudfront.CloudFrontWebDistribution(self, f"MyDistributionFront->main",
                                                            origin_configs=[cloudfront.SourceConfiguration(
                                                                s3_origin_source=cloudfront.S3OriginConfig(
                                                                    s3_bucket_source=source_bucket),
                                                                behaviors=[
                                                                    cloudfront.Behavior(is_default_behavior=True)], #use this configuration by deffault
                                                            )],
                                                            )

        git_source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            connection_arn="arn:aws:codestar-connections:eu-central-1:423704380788:connection/2f228b5f-a776-4312-876d-72a6c7e5d4d9",
            owner='oleksandr-yakov',
            repo='test_front',
            branch="main",   # use global env var : DEV_ENV=dev && cdk deploy <name stack> --profile oyakovenko-trainee
            action_name='GitHub_Source_Test-front-',
            output=git_source_output,
            trigger_on_push=True,
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name=f'CodeBuildFront',
            project=codebuild.PipelineProject(self, f"BuildProjectFront",
                                              build_spec=codebuild.BuildSpec.from_object({
                                                  "version": "0.2",
                                                  "phases": {
                                                      "install": {
                                                          "commands": [
                                                              "echo test ovsrd-trainee-front",
                                                              "npm install", #install depnds
                                                          ],
                                                      },
                                                      "build": {
                                                          "commands": [
                                                              "echo test ovsrd-trainee-front",
                                                              "npm build",   ##build proj
                                                          ],
                                                      },
                                                  },
                                                  # "artifacts": {
                                                  #     "files": [
                                                  #         "dist/**/*",
                                                  #     ],
                                                  # },
                                              }),
                                              ),
            input=git_source_output,
            outputs=[codepipeline.Artifact(artifact_name='output')]
        )

        invalidate_cloudfront_action = codepipeline_actions.CodeBuildAction(
            action_name="InvalidateCloudFront",
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

        pipeline = codepipeline.Pipeline(self, "FrontPipeline->main", stages=[
            codepipeline.StageProps(
                stage_name='Source',
                actions=[source_action]
            ),
            codepipeline.StageProps(
                stage_name='Build',
                actions=[build_action]
            ),
            codepipeline.StageProps(
                stage_name='DeployFrontS3CloudFront',
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



