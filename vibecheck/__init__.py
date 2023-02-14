from typing import Callable
import datetime
from datatops import Datatops
from ipywidgets import Button, HBox, Label, VBox, Layout, ButtonStyle, Textarea
from IPython.display import display


class ContentReview:
    def __init__(self, prompt: str, feedback_callback: Callable[[str, str], bool]):
        self._prompt = prompt
        self._button_pressed: str = None
        self._feedback_callback = feedback_callback

    def _submit(self, button_name: str, feedback: str):
        self._feedback_callback(button_name, feedback)

    def render(self):
        happy_button = Button(
            tooltip="Happy",
            icon="smile-o",
            layout=Layout(width="auto", height="auto"),
            style=ButtonStyle(button_color="#aaffaa"),
        )
        happy_button.add_class("happy")

        medium_button = Button(
            tooltip="Medium",
            icon="meh-o",
            layout=Layout(width="auto", height="auto"),
            style=ButtonStyle(button_color="#dddd77"),
        )
        medium_button.add_class("medium")

        sad_button = Button(
            tooltip="Sad",
            icon="frown-o",
            layout=Layout(width="auto", height="auto"),
            style=ButtonStyle(button_color="#ffaaaa"),
        )
        sad_button.add_class("sad")

        feedback_text = Textarea(
            placeholder="We want your feedback!",
            layout=Layout(width="auto", height="auto"),
        )

        submit_button = Button(
            description="Submit", layout=Layout(width="auto", height="auto")
        )

        feedback_container = HBox([feedback_text, submit_button])
        feedback_container.layout.display = "none"

        feedback_thanks = Label("Thanks for your feedback!")
        feedback_thanks.layout.display = "none"

        # When you click meh or sad, show the feedback text box
        def show_feedback_container_medium(b):
            self._button_pressed = "medium"
            # add border to the button
            medium_button.layout.border = "2px solid #666666"
            feedback_container.layout.display = "block"

        def show_feedback_container_sad(b):
            self._button_pressed = "sad"
            sad_button.layout.border = "2px solid #666666"
            feedback_container.layout.display = "block"

        medium_button.on_click(show_feedback_container_medium)
        sad_button.on_click(show_feedback_container_sad)

        def _submit_happy_feedback(b):
            self._submit("happy", "")
            happy_button.layout.border = "2px solid #666666"
            feedback_container.layout.display = "none"
            feedback_thanks.layout.display = "block"

        happy_button.on_click(_submit_happy_feedback)

        def _submit_unhappy_feedback(b):
            self._submit(self._button_pressed, feedback_text.value)
            feedback_container.layout.display = "none"
            feedback_thanks.layout.display = "block"

        submit_button.on_click(_submit_unhappy_feedback)

        return VBox(
            [
                Label(self._prompt),
                HBox([happy_button, medium_button, sad_button]),
                feedback_container,
                feedback_thanks,
            ]
        )


class ContentReviewContainer:
    def __init__(
        self, prompt: str, section_id: str, feedback_callback: Callable[[dict], bool]
    ):
        self._prompt = prompt
        self._section_id = section_id
        self._feedback_callback = feedback_callback
        self._content_review = ContentReview(prompt, self._submit)

    def _submit(self, button_name: str, feedback: str):
        self._feedback_callback(
            {
                "button_name": button_name,
                "feedback": feedback,
                "section_id": self._section_id,
                "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            }
        )

    def render(self):
        # return self._content_review.render()
        return display(self._content_review.render())


class DatatopsContentReviewContainer(ContentReviewContainer):
    def __init__(self, prompt: str, section_id: str, datatops_config: dict):
        self._prompt = prompt
        self._section_id = section_id
        self._content_review = ContentReview(prompt, self._submit)
        self._datatops = Datatops(datatops_config["url"])
        self._datatops_project = self._datatops.get_project(datatops_config["name"])
        super().__init__(prompt, section_id, self._submit)

    def _submit(self, button_name: str, feedback: str):
        self._datatops_project.store(
            {
                "button_name": button_name,
                "feedback": feedback,
                "section_id": self._section_id,
                "timestamp_utc": datetime.datetime.utcnow().isoformat(),
            }
        )
