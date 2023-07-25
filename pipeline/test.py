from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam
)
from constructs import Construct
from config import branch

class PipelineStackTest(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repo = codecommit.Repository.from_repository_name(
            self, "MyCodeCommitRepo",
            repository_name="fiesta-taco/ovsrd-trainee-front",
        )

        source_output = codepipeline.Artifact(artifact_name="SourceArtifact")
        git_source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit_Source",
            repository=repo,
            branch=branch,
            output=source_output,
        )

        build_project = codebuild.PipelineProject(self, "MyBuildProject",
            build_spec=codebuild.BuildSpec.from_object(
            {
                "version": "0.2",
                "phases": {
                    "Project setup": {
                        "commands": [
                            "echo test",
                        ],
                    },
                },
                "artifacts": {
                    "files": [
                        "Compiles and build and minifies for production/**/*",
                    ],
                },
            }),
        )

        build_role = aws_iam.Role(
            self, "MyBuildRole",
            assumed_by=aws_iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"),
            ]
        )

        build_project.add_to_role_policy(aws_iam.PolicyStatement(
            effect=aws_iam.Effect.ALLOW,
            actions=["codecommit:GitPull"],
            resources=[repo.repository_arn]
        ))

        build_output = codepipeline.Artifact(artifact_name="BuildOutput")
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="CodeBuild_Build",
            project=build_project,
            role=build_role,
            input=source_output,
            outputs=[build_output]
        )


        pipeline = codepipeline.Pipeline(self, "MyPipeline", stages=[
            codepipeline.StageProps(stage_name="Source", actions=[git_source_action]),
            codepipeline.StageProps(stage_name="Build", actions=[build_action]),
        ])
