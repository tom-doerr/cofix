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

Then run the script with the command to execute as an argument.
For example:

```
./cofix.py ./<your-program>.py
```

