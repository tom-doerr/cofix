# cofix
## What is it?

This script automatically fixes bugs in programs.
It does this by taking the command to execute as an argument and
analyzing the traceback after executing the command.
Then the script uses OpenAI's Codex to fix the line that causes
the bug.

## How to use it

First, install the `codex` module.

```
pip3 install openai
```
Next, add your authentication information in `AUTH.py`.

Build the docker container:
```
docker build docker -t cofix_docker
```

Then run the script with the command to execute as an argument.
For example:

```
docker run -it -v $PWD:/mounted cofix_image bash -c 'cd /mounted; ./cofix.py ./program_with_error.py' 
```

I use the docker environment for isolation, but this does not provide perfect protection from code interfering with your system.
