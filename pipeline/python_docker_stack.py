from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
)
from constructs import Construct
from config import connection_arn, branch


class PipelineStackDocker(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        git_source_output = codepipeline.Artifact()
        source_action = codepipeline_actions.CodeStarConnectionsSourceAction(
            connection_arn=connection_arn,
            owner='fiesta-taco',
            repo='ovsrd-trainee-back-docker',
            branch=branch,
            action_name=f'GitHub_Source-ovsrd-trainee-back-docker->{branch}',
            output=git_source_output,
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name=f'CodeBuildDocker->{branch}',
            project=codebuild.PipelineProject(self, f"BuildProjectDocker->{branch}",
                                              build_spec=codebuild.BuildSpec.from_object({
                                                  "version": "0.2",
                                                  "phases": {
                                                      "build": {
                                                          "commands": [
                                                              f"echo test ovsrd-trainee-back-docker branch={branch}",
                                                          ],
                                                      },
                                                  },
                                              }),
                                              ),
            input=git_source_output,
            outputs=[codepipeline.Artifact(artifact_name='output')]
        )
        pipeline = codepipeline.Pipeline(self, f"DockerPipeline->{branch}", stages=[
            codepipeline.StageProps(
                stage_name='Source',
                actions=[source_action]
            ),
            codepipeline.StageProps(
                stage_name='Build',
                actions=[build_action]
            ),
        ])
