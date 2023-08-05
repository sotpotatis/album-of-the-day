# Tasks

This directory contains tasks that are related to the website, for example to update album covers from Last.FM
and update daily rotations. These are run using a task runner (see below).

### Task runner

This directory also contains a task runner, which is a utility I wrote to run website-related tasks.
It ensures that the paths are correct and that Django models are accessible inside every task.
It can also update health status for each task to a remote service, with a modular interface
for adding new ones.

#### Where to find the task runner

Go to `systemd/task_runner` to see the actual task runner.