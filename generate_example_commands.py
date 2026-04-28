#!/usr/bin/env python3

import subprocess
import sys


def generate_example_commands():
    """
    Generates example commands for a given command/tool.
    """
    print("Welcome to the Example Command Generator!")
    print("-" * 30)

    # --- Get the path to the command/tool ---
    while True:
        command_path = input(
            "Please enter the full path to your command/tool "
            "(e.g., 'ls', '/usr/bin/grep', 'python my_script.py'): "
        ).strip()
        if not command_path:
            print("Command path cannot be empty. Please try again.")
        else:
            # A simple check to see if the command might exist.
            # This is not foolproof but helps catch obvious typos.
            try:
                # Try to execute with --help or -h to see if it's a valid command.
                # We'll run it in a subprocess and capture output, then discard it.
                # If it fails, it's likely not a valid command or doesn't have help.
                subprocess.run(
                    [command_path, "--help"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                break  # Command seems valid, exit loop
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    subprocess.run(
                        [command_path, "-h"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    break  # Command seems valid, exit loop
                except (FileNotFoundError, subprocess.CalledProcessError):
                    print(
                        f"Could not find or execute '{command_path}' with --help or -h."
                    )
                    print(
                        "Please ensure the path is correct and the command is executable."
                    )
                    # You might want to add more sophisticated checks here,
                    # like checking if it's in the PATH if no path is given.

    # --- Get the number of example commands ---
    while True:
        try:
            num_examples = int(input("How many example commands do you want to generate? "))
            if num_examples <= 0:
                print("Please enter a positive number.")
            else:
                break
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    print(f"\nGenerating {num_examples} example command(s) for '{command_path}'...")
    print("-" * 30)

    # --- Generate Example Commands (Developer State - Placeholder Logic) ---
    # This is the core "developer state" part. Here, you'll need to
    # implement logic that understands how to construct example commands.
    # This will be HIGHLY dependent on the type of command/tool you're targeting.

    # For demonstration purposes, we'll use a very simple approach:
    # appending common flags or arguments.
    # In a real-world scenario, you'd likely have:
    # 1. A way to describe the command's purpose and arguments.
    # 2. A more sophisticated generation mechanism.

    # Common example arguments to append. You'll want to tailor these.
    example_arguments = [
        "--verbose",
        "-l",
        "--force",
        "-i",
        "--output results.txt",
        "input.txt",
        "--help",
        "-v",
        "--dry-run",
        "-f",
        "--config /etc/myapp.conf",
        "data.csv",
    ]

    generated_commands = []
    for i in range(num_examples):
        # Simple example: Take the command path and append a few random arguments.
        command_parts = [command_path]
        # Let's try to add a couple of arguments for each command.
        num_args_to_add = min(len(example_arguments), i % 3 + 1)  # Add 1, 2, or 3 args
        for _ in range(num_args_to_add):
            # Simple way to pick an argument. More advanced would be smarter selection.
            arg_index = (i + len(generated_commands)) % len(example_arguments)
            command_parts.append(example_arguments[arg_index])

        generated_commands.append(" ".join(command_parts))

    # --- Display the generated commands ---
    if generated_commands:
        print("Here are your example commands:")
        for i, cmd in enumerate(generated_commands):
            print(f"{i + 1}. {cmd}")
    else:
        print("No example commands were generated.")

    print("\nGeneration complete!")


if __name__ == "__main__":
    # Check Python version for compatibility (e.g., for subprocess.run)
    if sys.version_info < (3, 5):
        print("This script requires Python 3.5 or later.")
        sys.exit(1)

    generate_example_commands()
