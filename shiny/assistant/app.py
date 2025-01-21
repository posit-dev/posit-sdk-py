import os
import pathlib
import tempfile
import urllib.parse

import chatlas
import faicons

from shiny import App, Inputs, reactive, render, session, ui

app_ui = ui.page_fillable(
    ui.h1(
        "SDK Assistant",
        ui.input_action_link("info_link", label=None, icon=faicons.icon_svg("circle-info")),
        ui.output_text("cost", inline=True),
    ),
    ui.output_ui("new_gh_issue", inline=True),
    ui.chat_ui("chat", placeholder="Ask your posit-SDK questions here..."),
    ui.tags.style(
        """
        #info_link {
            font-size: medium;
            vertical-align: super;
            margin-left: 10px;
        }
        #cost {
            color: lightgrey;
            font-size: medium;
            vertical-align: middle;
        }
        .sdk_suggested_prompt {
            cursor: pointer;
            border-radius: 0.5em;
            display: list-item;
        }
        .external-link {
            cursor: alias;
        }
        #new_gh_issue {
            position: absolute;
            right: 15px;
            top: 15px;
            height: 25px;
        }
        """
    ),
    ui.tags.script(
        """
        $(() => {
            $("body").click(function(e) {
                if (!$(e.target).hasClass("sdk_suggested_prompt")) {
                    return;
                }
                window.Shiny.setInputValue("new_sdk_prompt", $(e.target).text());
            });
        })
        window.Shiny.addCustomMessageHandler("submit-chat", function(message) {
            const enterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
            });

            // Dispatch the 'Enter' event on the input element
            console.log("Dispatching Enter event", message);
            document.querySelector("#" + message['id'] + " textarea#chat_user_input").dispatchEvent(enterEvent);
        });

        """
    ),
    fillable_mobile=True,
)


def server(input: Inputs):  # noqa: A002
    aws_model = os.getenv("AWS_MODEL", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    chat = chatlas.ChatBedrockAnthropic(model=aws_model, aws_region=aws_region)
    prompt_file = pathlib.Path(__file__).parent / "_prompt.xml"
    if not os.path.exists(prompt_file):
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file} ; Please run `make shiny` to generate it."
        )
    with open(prompt_file, "r") as f:
        chat.system_prompt = f.read()

    chat_ui = ui.Chat(
        "chat",
        # messages=[{"role": turn.role, "content": turn.text} for turn in chat.get_turns()],
    )

    async def submit_chat(new_value: str):
        chat_ui.update_user_input(value=new_value)

        local_session = session.require_active_session(None)
        await local_session.send_custom_message("submit-chat", {"id": "chat"})

    @render.text
    def cost():
        _ = chat_ui.messages()

        tokens = chat.tokens("cumulative")
        if len(tokens) == 0:
            return None

        cost = sum(
            [
                # Input + Output
                (token[0] * 0.003 / 1000.0) + (token[1] * 0.015 / 1000.0)
                for token in tokens
                if token is not None
            ]
        )
        ans = "$%s" % float("%.3g" % cost)
        while len(ans) < 5:
            ans = ans + "0"
        return ans

    @render.ui
    def new_gh_issue():
        messages = chat_ui.messages()
        for message in messages:
            if message["role"] == "assistant":
                break
        else:
            # No LLM response found. Return
            return

        first_message_content: str = str(messages[0].get("content", ""))

        with tempfile.TemporaryDirectory() as tmpdirname:
            export_path = tmpdirname + "/chat_export.md"
            chat.export(export_path, include="all", include_system_prompt=False)

            with open(export_path, "r") as f:
                exported_content = f.read()

        body = f"""
**First message:**
```
{first_message_content}
```

**Desired outcome:**

Please describe what you would like to achieve in `posit-sdk`. Any additional context, code, or examples are welcome!

```python
from posit.connect import Client
client = Client()

# Your code here
```

-----------------------------------------------

<details>
<summary>Chat Log</summary>

````markdown
{exported_content}
````
</details>
"""

        title = (
            "SDK Assistant: `"
            + (
                first_message_content
                if len(first_message_content) <= 50
                else (first_message_content[:50] + "...")
            )
            + "`"
        )

        new_issue_url = (
            "https://github.com/posit-dev/posit-sdk-py/issues/new?"
            + urllib.parse.urlencode(
                {
                    "title": title,
                    "labels": ["template idea"],
                    "body": body,
                }
            )
        )

        # if chat_ui.messages(format="anthropic")
        return ui.a(
            ui.img(src="new_gh_issue.svg", alt="New GitHub Issue", height="100%"),
            title="Submit script example to Posit SDK",
            class_="external-link",
            href=new_issue_url,
            target="_blank",
        )

    @chat_ui.on_user_submit
    async def _():
        user_input = chat_ui.user_input()
        if user_input is None:
            return
        await chat_ui.append_message_stream(
            await chat.stream_async(
                user_input,
                echo="all",
            )
        )

    @reactive.effect
    @reactive.event(input.new_sdk_prompt)
    async def _():
        await submit_chat(input.new_sdk_prompt())

    @reactive.effect
    async def _init_chat_on_load():
        await submit_chat("What are the pieces of Posit connect and how do they fit together?")

        # Remove the effect after the first run
        _init_chat_on_load.destroy()

    @reactive.effect
    @reactive.event(input.info_link)
    async def _():
        modal = ui.modal(
            ui.h1("Information"),
            ui.h3("Model"),
            ui.pre(
                f"Model: {aws_model}\nRegion: {aws_region}",
            ),
            ui.h3("System prompt"),
            ui.pre(chat.system_prompt),
            easy_close=True,
            size="xl",
        )
        ui.modal_show(modal)


app = App(
    app_ui,
    server,
    static_assets=pathlib.Path(__file__).parent / "www",
)
