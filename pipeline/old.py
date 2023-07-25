from aws_cdk import (
    Stack,
    pipelines,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
)
import aws_cdk as cdk
from constructs import Construct
from config import connection_arn, branch


class PipelineStackOld(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_bucket = s3.Bucket(self, "SourceBucket", removal_policy=cdk.RemovalPolicy.DESTROY)

        distribution = cloudfront.CloudFrontWebDistribution(self, "MyDistribution",
                                                            origin_configs=[cloudfront.SourceConfiguration(
                                                                s3_origin_source=cloudfront.S3OriginConfig(
                                                                    s3_bucket_source=source_bucket),
                                                                behaviors=[
                                                                    cloudfront.Behavior(is_default_behavior=True)],
                                                            )],
                                                            )

        git_source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            connection_arn=connection_arn,
            owner='fiesta-taco',
            repo='ovsrd-trainee-front',
            branch=branch,
            action_name='GitHub_Source',
            output=git_source_output,
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name='CodeBuild',
            project=codebuild.PipelineProject(self, "MyBuildProject",
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "phases": {
                        "build": {
                            "commands": [
                                "echo test",
                            ],
                        },
                    },
                    "artifacts": {
                        "files": [
                            "/build",
                        ],
                    },
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

        pipeline = codepipeline.Pipeline(self, "OldPipeline", stages=[
            codepipeline.StageProps(
                stage_name='Source',
                actions=[source_action]
            ),
            codepipeline.StageProps(
                stage_name='Build',
                actions=[build_action]
            ),
            codepipeline.StageProps(
                stage_name='Deploy',
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
