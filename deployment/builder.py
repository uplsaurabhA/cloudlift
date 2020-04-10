# class DockerBuilder(object):
#     def __init__(self, name, environment, env_sample_file, version=None,
#                  working_dir='.'):
#         self.name = name
#         self.environment = environment
#         if env_sample_file is not None:
#             self.env_sample_file = env_sample_file
#         else:
#             self.env_sample_file = './env.sample'
#         self.version = version
#         self.ecr_client = boto3.session.Session(region_name=self.region).client('ecr')
#         self.working_dir = working_dir
