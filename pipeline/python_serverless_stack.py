from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
)
from constructs import Construct
from config import connection_arn, branch


class PipelineStackServerless(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        git_source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            connection_arn=connection_arn,
            owner='fiesta-taco',
            repo='ovsrd-trainee-back-serverless',
            branch=branch,
            action_name='GitHub_Source_ovsrd-trainee-back-serverless',
            output=git_source_output,
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name='CodeBuildServerless',
            project=codebuild.PipelineProject(self, "MyBuildProjectServerless",
                                              build_spec=codebuild.BuildSpec.from_object({
                                                  "version": "0.2",
                                                  "phases": {
                                                      "build": {
                                                          "commands": [
                                                              f"echo test ovsrd-trainee-back-serverless {branch}",
                                                          ],
                                                      },
                                                  },
                                              }),
                                              ),
            input=git_source_output,
            outputs=[codepipeline.Artifact(artifact_name='output')]
        )

        pipeline = codepipeline.Pipeline(self, "ServerlessPipeline", stages=[
            codepipeline.StageProps(
                stage_name='Source',
                actions=[source_action]
            ),
            codepipeline.StageProps(
                stage_name='Build',
                actions=[build_action]
            ),
        ])




