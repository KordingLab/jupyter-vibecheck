from typing import Callable, Optional, Protocol
import datetime
from datatops import Datatops
from ipywidgets import (
    Button,
    HBox,
    Label,
    VBox,
    Layout,
    ButtonStyle,
    Textarea,
    HTML,
    Output,
)
from IPython.display import display
from collections import Counter


class DatatopsButton(Protocol):
    _name: str

    @property
    def name(self):
        return self._name

    def widget_factory(self):
        pass


class TrafficLightButton:
    def __init__(
        self, text: str, color: str = "#dedede", description: Optional[str] = None
    ):
        self._name = text
        self._description = text if description is None else description
        self._color = color

    def widget_factory(self):
        btn = Button(
            tooltip=self._description,
            description=self._name,
            layout=Layout(width="auto", height="auto"),
            style=ButtonStyle(button_color=self._color, font_size="2em"),
        )
        btn.add_class(self._description)
        btn.layout.padding = "0.5em"
        return btn


class ContentReview:
    def __init__(
        self,
        prompt: str,
        feedback_callback: Callable[[str, str], bool],
        show_medium: bool = True,
    ):
        self._prompt = prompt
        self._button_pressed: str = None
        self._feedback_callback = feedback_callback
        self._show_medium = show_medium

    def _submit(self, button_name: str, feedback: str):
        self._feedback_callback(button_name, feedback)

    def render(self):
        happy_button = TrafficLightButton("🙂", "#aaffaa", "happy").widget_factory()
        medium_button = TrafficLightButton("😐", "#dddd77", "medium").widget_factory()
        sad_button = TrafficLightButton("🙁", "#ffaaaa", "sad").widget_factory()

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

        buttons = (
            [
                happy_button,
                medium_button,
                sad_button,
            ]
            if self._show_medium
            else [happy_button, sad_button]
        )

        rows = [HBox(buttons), feedback_container, feedback_thanks]
        return VBox([Label(self._prompt), *rows]) if self._prompt else VBox(rows)


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
        self._datatops = Datatops(datatops_config.pop("url"))
        self._datatops_project = self._datatops.get_project(**datatops_config)
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

    def _has_admin_access(self):
        return self._datatops_project.admin_key is not None

    def _admin_results(self):
        # {'__datatops_project': 'public_testbed',
        # '__datatops_timestamp_iso': '1682534910', 'button_name': 'happy',
        # 'feedback': '', 'section_id': 'Learning Datatops',
        # 'timestamp_utc': '2023-04-26T18:48:31.836088'}
        results = [
            d
            for d in self._datatops_project.list_data()
            if d["section_id"] == self._section_id
        ]
        button_counter = Counter([d["button_name"] for d in results])

        try:
            import matplotlib.pyplot as plt
        except ModuleNotFoundError:
            print("Matplotlib is not installed, falling back on basic display")
            return HTML(
                f"""
                <table>
                    <tr>
                        <th>Happy</th>
                        <th>Medium</th>
                        <th>Sad</th>
                    </tr>
                    <tr>
                        <td>{str(button_counter['happy'])}</td>
                        <td>{str(button_counter['medium'])}</td>
                        <td>{str(button_counter['sad'])}</td>
                    </tr>
                    <tr>
                        <td>{str(button_counter['happy'] / len(results) * 100)}%</td>
                        <td>{str(button_counter['medium'] / len(results) * 100)}%</td>
                        <td>{str(button_counter['sad'] / len(results) * 100)}%</td>
                    </tr>
            """
            )

        fig, ax = plt.subplots()
        ax.bar(
            ["happy", "medium", "sad"],
            [button_counter["happy"], button_counter["medium"], button_counter["sad"]],
        )
        ax.set_ylabel("Count")
        ax.set_title("Content Review Results")
        plt.show()
        return Output()

    def render(self):
        return display(
            VBox(
                [self._content_review.render()]
                + ([self._admin_results()] if self._has_admin_access() else [])
            )
        )
