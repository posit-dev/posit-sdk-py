import os
import pathlib

import chatlas
import faicons

from shiny import App, Inputs, reactive, render, session, ui

app_ui = ui.page_fillable(
    ui.h1(
        "SDK Assistant",
        ui.input_action_link("info_link", label=None, icon=faicons.icon_svg("circle-info")),
        ui.output_text("cost", inline=True),
    ),
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
        """
    ),
    ui.tags.script(
        """
        $(() => {
            $("body").click(function(e) {
                console.log("click", e, e.target, $(e.target).hasClass("sdk_suggested_prompt"));
                if (!$(e.target).hasClass("sdk_suggested_prompt")) {
                    return;
                }
                window.Shiny.setInputValue("new_sdk_prompt", $(e.target).text());
            });
        })
        Shiny.addCustomMessageHandler("submit-chat", function(message) {
            const enterEvent = new KeyboardEvent('keydown', {
                key: 'Enter',
                code: 'Enter',
                keyCode: 13,
                which: 13,
            });

            // Dispatch the 'Enter' event on the input element
            console.log("Dispatching Enter event");
            document.querySelector("#chat textarea#chat_user_input").dispatchEvent(enterEvent);
        });

        """
    ),
    fillable_mobile=True,
)


def server(input: Inputs):  # noqa: A002
    aws_model = os.getenv("AWS_MODEL", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    chat = chatlas.ChatBedrockAnthropic(model=aws_model, aws_region=aws_region)
    with open(pathlib.Path(__file__).parent / "prompt.xml", "r") as f:
        chat.system_prompt = f.read()

    chat_ui = ui.Chat(
        "chat",
        # messages=[{"role": turn.role, "content": turn.text} for turn in chat.get_turns()],
    )

    @render.text
    def cost():
        _ = chat_ui.messages()

        cost = sum(
            [
                # Input + Output
                (token[0] * 0.003 / 1000.0) + (token[1] * 0.015 / 1000.0)
                for token in chat.tokens("cumulative")
                if token is not None
            ]
        )
        return "$%s" % float("%.3g" % cost)

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
        chat_ui.update_user_input(value=input.new_sdk_prompt())
        local_session = session.require_active_session(None)
        await local_session.send_custom_message("submit-chat", {})

    @reactive.effect
    async def _init_chat():
        chat_ui.update_user_input(value="Hello")

        local_session = session.require_active_session(None)
        await local_session.send_custom_message("submit-chat", {})

        _init_chat.destroy()

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


app = App(app_ui, server)
