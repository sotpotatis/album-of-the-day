# Task runner
To simplify path handling and task tracking, I implemented a "task runner". It does the following:

1. Map a task ID to its filepath: for example `update_daily_rotations` --> `/home/username/album_of_the_day/../update_daily_rotations.py`
2. Report task success (or failure) to a remote tracking server (currently, [Healthchecks](https://healthchecks.io) is supported)

This mainly solves that you don't have to change all service files in case you move a script somewhere else. Simply change the task runner config
and you're good to go!

### Example usage

To run a single task:


`python task_runner.py <name_of_task_to_run>`

##### Infinite task runner

The infinite task runner works similar to the way cron works (but much less stable and only runs when the server
is running). It uses the configuration file to schedule tasks to run at certain times.

After checking that the configuration file si what you want:

`python task_runner_infinite.py`