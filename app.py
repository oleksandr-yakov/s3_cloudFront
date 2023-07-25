#!/usr/bin/env python3
import aws_cdk as cdk
from pipeline.python_front_stack import PipelineStackFront
from pipeline.python_docker_stack import PipelineStackDocker
from pipeline.python_serverless_stack import PipelineStackServerless
from config import account, region


app = cdk.App()

PipelineStackFront(app, "PipelineStackFront",
                        env=cdk.Environment(account=account, region=region),
                        stack_name='front-stack')

PipelineStackServerless(app, "PipelineStackServerless",
                        env=cdk.Environment(account=account, region=region),
                        stack_name='serverless-stack')

PipelineStackDocker(app, "PipelineStackDocker",
                        env=cdk.Environment(account=account, region=region),
                        stack_name='docker-stack')

app.synth()


#from pipeline.old import PipelineStackOld
#from pipeline.test import PipelineStackTest
#PipelineStackTest(app, "PipelineStackTest",
#                         env=cdk.Environment(account=account, region=region),
#                         stack_name='front-stack')
#PipelineStackOld(app, "PipelineStackOld",
#                          env=cdk.Environment(account=account, region=region),
#                          stack_name='old-stack')