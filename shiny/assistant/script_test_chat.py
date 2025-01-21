from __future__ import annotations

import asyncio
import os
import pathlib

import chatlas

# # Set working directory to the root of the repository
# repo_root = pathlib.Path(__file__)
# while not os.path.exists(repo_root / "pyproject.toml"):
#     repo_root = repo_root.parent
# os.chdir(repo_root)

# Set to _here_
os.chdir(pathlib.Path(__file__).parent)


async def main() -> None:
    print("Running chatlas")
    aws_model = os.getenv("AWS_MODEL", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    chat = chatlas.ChatBedrockAnthropic(model=aws_model, aws_region=aws_region)

    with open("prompt.xml", "r") as f:
        chat.system_prompt = f.read()

    prompt = "Which groups do I belong to?"
    # Worked!

    # prompt = "How many users have been active within the last 30 days."
    # # Discovers that `Event`s sometimes do not have a user_guid associated with them.
    # # Once adjusted to account for that, it works great!

    # prompt = "Which python content items that I have deployed are using version 2 or later of the Requests package?"
    # # Has a LOT of trouble finding "my" content items. All prompts currently return for all content items.
    # # Even adjusting for `client.me.content.find()`, I run into a server error related to request:
    # # GET v1/content/38be0f3e-9cca-4e7a-8ea8-0990d989786f/packages params={'language': 'python', 'name': 'requests'} response=<Response [204]> response.content=b''
    # # IDK why this one breaks and many others pass

    # prompt = 'List all processes associated with "My Content".'
    # # Worked great once I changed `content.jobs.find()` to `content.jobs.fetch()`!

    # prompt = "Get me the group of users that publish the most quarto content in the last week"
    # prompt = "Get me the set of users that published the most quarto content in the last 7 days"
    # # Worked great!

    ans = await chat.stream_async(prompt, echo="all")

    content = await ans.get_content()
    print("Content:\n", content)
    print("--\n")

    cost = sum(
        [
            # Input + Output
            (token[0] * 0.003 / 1000.0) + (token[1] * 0.015 / 1000.0)
            for token in chat.tokens("cumulative")
            if token is not None
        ]
    )
    # Example cost calculation:
    # Link: https://aws.amazon.com/bedrock/pricing/#Pricing_details
    # cost = 0.003 * input + 0.015 * output + 0.0003 * cached_input
    # Our input is ~30k of the 35k
    # Our output is < 500
    # cost = 0.003 * (35 - 30) + 0.015 * 500/1000 + 0.0003 * 30
    # cost = 0.0315
    print("Token count: ", chat.tokens("cumulative"))
    print("Cost: ", "$%s" % float("%.3g" % cost))

    # Save to ./chatlas folder
    pathlib.Path("chatlas").mkdir(exist_ok=True)
    chat.export(pathlib.Path(__file__).parent / "chatlas" / f"{prompt}.md", overwrite=True)


if __name__ == "__main__":
    asyncio.run(main())

    # Current output is 147k chars (29k tokens)
    # Replacing all `    ` with `  ` would reduce it to 127k chars (~25k tokens)
    # Bedrock Anthropic Claude states inputs to be less than 180k tokens.
    # So, we are good to go.

    # Next steps:
    # √ 0. Token count
    # √ 0. Prompts to try:
    #   * Which applications are using version 2 or later of the Requests package?
    #   * How many users have been active within the last 30 days.
    #   * List all processes associated with "My Content". (This functionality doesn't exist in the SDK, so see it makes up an answer)
    # √ 1. prompt: "Get me the group of users that publish the most quarto content in the last week."
    #   * Possibly need to prompt about using Polars to help with intermediate steps.
    # 1. Make app for demo
    # 2. Add API routes, methods, descriptions and return types in a quick document
