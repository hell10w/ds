# import os
#
# from ds.context import TestExecutorMixin
# from ds.presets.docker_base import mixins
# from ds.presets.docker_base import commands
# from ds.presets.docker_base import DockerContext
# from ds.executor import TestExecutor
#
#
# def override_run_option_by_attr(mixin, attr, run_option=None, default=None):
#     if issubclass(DockerContext, mixin):
#         bases = (DockerContext, )
#     else:
#         bases = (mixin, DockerContext, )
#
#     run_option = run_option or attr
#
#     Context = type('Context', bases, {})
#     context = Context()
#     assert context.get_run_options().get(run_option) == default
#
#     Context = type('Context', bases, {
#         attr: None,
#     })
#     context = Context()
#     assert context.get_run_options().get(run_option) == None
#
#     value = 'TEST'
#     Context = type('Context', bases, {
#         attr: value,
#     })
#     context = Context()
#     assert context.get_run_options().get(run_option) == value
#
#
# def check_command_invoke(context_class, command_name, invoke_args, execute_args):
#     class Context(TestExecutorMixin, context_class):
#         pass
#     context = context_class()
#     context[command_name](invoke_args)
#     context.executor.commit()
#     assert context.executor.logs[0] == ([TestExecutor.CALL] + execute_args)
#
#
# def check_command_exists(mixin, command_class):
#     if issubclass(DockerContext, mixin):
#         bases = (DockerContext, )
#     else:
#         bases = (mixin, DockerContext, )
#
#     Context = type('Context', bases, {})
#     context = Context()
#     command = command_class(context)
#     assert context[command.get_name()]
#
#
# def test_user_mixin():
#     assert not issubclass(DockerContext, mixins.UserMixin)
#     override_run_option_by_attr(mixins.UserMixin, 'container_user',
#                                 'user', os.getuid())
#
#
# def test_network_mixin():
#     assert issubclass(DockerContext, mixins.NetworkMixin)
#     override_run_option_by_attr(mixins.NetworkMixin, 'network', 'network')
#
#
# def test_environment_mixin():
#     assert issubclass(DockerContext, mixins.EnvironmentMixin)
#     override_run_option_by_attr(mixins.NetworkMixin, 'container_environment',
#                                 'environment', default={})
#
#     # class Context(DockerContext):
#     #     pass
#     # context = Context()
#     # assert context.get_run_options().get('environment') == {}
#     #
#     # envs = {'a': 1}
#     #
#     # class Context(DockerContext):
#     #     def get_envs(self):
#     #         return envs
#     # context = Context()
#     # assert context.get_run_options().get('environment') == envs
#
#
# def test_mounts_mixin():
#     pass
#
#
# def test_home_mounts_mixin():
#     pass
#
#
# def test_working_dir_mixin():
#     assert not issubclass(DockerContext, mixins.WorkingDirMixin)
#     override_run_option_by_attr(mixins.WorkingDirMixin, 'working_dir',
#                                 default='/app/')
#
#
# def test_project_mounts_mixin():
#     pass
#
#
# def test_shell_mixin():
#     assert issubclass(DockerContext, mixins.ShellMixin)
#     # override_run_option_by_attr(mixins.ShellMixin, 'shell_entry',
#     #                             default='/bin/bash')
#     check_command_exists(mixins.ShellMixin, commands.Shell)
#     check_command_exists(mixins.ShellMixin, commands.RootShell)
#
#     class Context(mixins.ShellMixin, DockerContext):
#         pass
#     check_command_invoke(Context, 'shell', ('docker', 'exec', ''))
