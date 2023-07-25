import os


connection_arn = "arn:aws:codestar-connections:eu-central-1:666398651410:connection/46c6e5d6-ba43-49e9-bb58-cf9bd4c97755" #           arn:aws:codestar-connections:eu-central-1:666398651410:connection/c3334e5c-add7-4e56-a34e-e0baab5c5a7e
account = '666398651410'
region = 'eu-central-1'



# repo_string = os.environ.get('REPO_STR')
# print(repo_string)
repo_string = "oleksandr-yakov/pipeline"   #fiesta-taco/ovsrd-trainee-front


branch = os.environ.get('DEV_ENV')
# print(branch)
#branch = "main"

