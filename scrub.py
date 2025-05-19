import re
import uuid
import json
import spacy
import streamlit as st
from streamlit import components


def sample_email_text():
    return """
Subject: Dog Tales Volume I – Story Assignments and Tone Discussion

From: Samantha Wills samantha@canineclassics.org
To: Mark Bell, Dana Cho, Rachel Griggs, Tyler Jensen
Date: January 3, 2025

Hi team,

Excited to kick off our anthology Dog Tales: Stories of Loyalty, Love, and Mud.

Let’s clarify direction: warm, heartful, slightly humorous stories about dogs and their humans. Nothing too tragic — we want readers to smile and cry a little, but not need therapy after each story.

Story assignments:

Dana: "The Shepherd of Hollow Hill" – a sheepdog who guides a boy home during a blizzard.

Mark: "Fetch" – a retriever who keeps bringing home strange objects.

Rachel: "The Last Biscuit" – old dog, retirement home, gentle reflection.

Tyler: "Snarl" – feral street dog slowly learns to trust.

Please send first drafts by Feb 1. And no, Tyler, your dog can’t literally kill a man in chapter one. Let’s keep it PG, please.

– Sam

Subject: Re: Dog Tales Volume I – Story Assignments and Tone Discussion

From: Tyler Jensen tyler.j@feraldreams.net
To: Samantha Wills
CC: Team
Date: January 3
"""


class DataPseudonymizer:
    def __init__(self):
        self.uid = str(uuid.uuid4())
        self.mapping = {}
        self.nlp = spacy.load("en_core_web_trf")
        self.supported_nlp_types = {
            "PERSON",
            "GPE",
            "ORG",
            "TIME",
            "MONEY",
            "FAC",
            "NORP",
            "WORK_OF_ART",
            "EVENT",
        }
        self.token_count = 0
        self.sensitive_patterns = {
            "email": r"[\w.-]+@[\w.-]+",
            "phone": r"\b\d{3}[-.]\d{3}[-.]\d{4}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "cc": r"\b(?:\d[ -]*?){13,16}\b",
        }

    def _generate_token(self, label):
        token = f"[[[{label.upper()}_{self.token_count}]]]"

        self.token_count += 1
        return token

    def reset(self):
        self.token_count = 0
        self.mapping = {}

    def pseudonymize_text(self, text):

        self.sort_mapping()
        # Step 3: Ensure all values in self.mapping are pseudonymized (search and replace)
        for original, token in self.mapping.items():
            text = text.replace(original, token)
        return text

    def depseudonymize_text(self, text):

        reverse_mapping = {v: k for k, v in self.mapping.items()}
        for token, original in reverse_mapping.items():
            text = text.replace(token, original)
        return text

    def populate_mapping(self, text):

        patterns = self.sensitive_patterns
        for label, pattern in patterns.items():
            for match in re.findall(pattern, text):
                if match not in self.mapping:
                    self.mapping[match] = self._generate_token(label)
        doc = self.nlp(text)
        doc.ents = sorted(doc.ents, key=len, reverse=True)
        for ent in doc.ents:
            if ent.label_ in self.supported_nlp_types:
                if ent.text not in self.mapping:
                    self.mapping[ent.text] = self._generate_token(ent.label_)

    def sort_mapping(self):

        self.mapping = dict(
            sorted(self.mapping.items(), key=lambda item: len(item[0]), reverse=True)
        )

    def get_mapping(self):

        self.sort_mapping()
        return json.dumps(self.mapping, indent=2)

    def update_mapping(self, new_entries):

        self.mapping.update(new_entries)
        self.sort_mapping()

    def set_mapping(self, new_mapping):

        self.mapping = new_mapping
        self.sort_mapping()


# Streamlit App
st.set_page_config(page_title="Pseudonymizer", layout="wide", page_icon="🔐")


# --- Page Title and Description ---
st.title("🎭 Data Pseudonymizer")
st.markdown(
    """
Easily replace sensitive data in plain text using automated pseudonymization.
Customize or inspect the mapping table and reverse changes as needed.
"""
)

# --- Initialize Pseudonymizer ---
if st.session_state.get("pseudonymizer", None) is None:
    st.session_state.pseudonymizer = DataPseudonymizer()
    pseudonymizer = st.session_state.pseudonymizer
else:
    pseudonymizer = st.session_state.pseudonymizer


# --- Initialize session state ---
if "plain_text" not in st.session_state:

    st.session_state.plain_text = sample_email_text()
if "pseudonymized_text" not in st.session_state:

    pseudonymizer.populate_mapping(st.session_state.plain_text)
    st.session_state.pseudonymized_text = pseudonymizer.pseudonymize_text(
        st.session_state.plain_text
    )
if "mapping_text" not in st.session_state:

    st.session_state.mapping_text = pseudonymizer.get_mapping()


# --- Update functions ---
def update_from_plain_text():

    pseudonymizer.populate_mapping(st.session_state["plain_text"])
    st.session_state["pseudonymized_text"] = pseudonymizer.pseudonymize_text(
        st.session_state["plain_text"]
    )
    st.session_state["mapping_text"] = pseudonymizer.get_mapping()


def update_from_pseudonymized_text():

    # pseudonymizer.update_mapping(json.loads(st.session_state["mapping_text"]))
    st.session_state["plain_text"] = pseudonymizer.depseudonymize_text(
        st.session_state["pseudonymized_text"]
    )


def update_from_mapping_text():

    pseudonymizer.set_mapping(json.loads(st.session_state["mapping_text"]))
    st.session_state["pseudonymized_text"] = pseudonymizer.pseudonymize_text(
        st.session_state["plain_text"]
    )
    st.session_state["mapping_text"] = pseudonymizer.get_mapping()


def refresh_from_plain_text():

    st.session_state["pseudonymized_text"] = pseudonymizer.pseudonymize_text(
        st.session_state["plain_text"]
    )


def refresh_from_pseudonymized_text():

    update_from_mapping_text()
    st.session_state["plain_text"] = pseudonymizer.depseudonymize_text(
        st.session_state["pseudonymized_text"]
    )


def refresh_from_mapping_text():

    pseudonymizer.set_mapping(json.loads(st.session_state["mapping_text"]))
    st.session_state["mapping_text"] = pseudonymizer.get_mapping()


def add_to_mapping():

    entry = st.session_state.get("new_mapping_entry", "")
    label = st.session_state.get("new_mapping_label", "CUSTOM")
    if entry:
        token = f"[[[{label.upper()}_{uuid.uuid4().hex[:6]}]]]"

        pseudonymizer.update_mapping({entry: token})
        st.session_state["mapping_text"] = pseudonymizer.get_mapping()
        st.session_state["new_mapping_entry"] = ""
        st.session_state["pseudonymized_text"] = pseudonymizer.pseudonymize_text(
            st.session_state["plain_text"]
        )


def clear_plain_field():
    st.session_state["plain_text"] = ""


def clear_mapping_field():
    st.session_state["mapping_text"] = "{}"
    pseudonymizer.reset()


def clear_pseu_field():
    st.session_state["pseudonymized_text"] = ""


def clear_all_fields():
    clear_plain_field()
    clear_mapping_field()
    clear_pseu_field()

    # --- Unified Column Layout ---


col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📄 Plain Text")
    st.text_area("Paste or edit plain text:", key="plain_text", height=400)
    st.button(
        "▶️ Run SpaCy and Update Pseu and Mapping",
        on_click=update_from_plain_text,
        key="run_plain",
    )
    st.button("🔄 Update Pseu", on_click=refresh_from_plain_text, key="refresh_plain")
    st.button(
        "Clear Plain Text",
        on_click=clear_plain_field,
        key="clear_all_fields1",
        icon="🚫",
    )
    st.button("Reset", on_click=clear_all_fields, key="reset1", icon="❌")

with col2:
    st.subheader("🧩 Mapping")
    st.text_area("Edit token mappings:", key="mapping_text", height=400)
    st.button(
        "▶️ Update Pseu and Mapping",
        on_click=update_from_mapping_text,
        key="run_mapping",
    )
    st.button(
        "🔄 Update Mapping", on_click=refresh_from_mapping_text, key="refresh_mapping"
    )
    st.button(
        "Clear Mapping",
        on_click=clear_mapping_field,
        key="clear_all_fields2",
        icon="🚫",
    )
    st.button("Reset", on_click=clear_all_fields, key="reset2", icon="❌")

with col3:
    st.subheader("🛡️ Pseudonymized")
    st.text_area(
        "View or edit pseudonymized output:", key="pseudonymized_text", height=400
    )
    st.button(
        "▶️ Update Plain (Update Mapping First)",
        on_click=update_from_pseudonymized_text,
        key="run_pseudo",
    )
    st.button(
        "🔄 Refresh", on_click=refresh_from_pseudonymized_text, key="refresh_pseudo"
    )
    st.button(
        "Clear Pseudonymized Text",
        on_click=clear_pseu_field,
        key="clear_all_fields3",
        icon="🚫",
    )
    st.button("Reset", on_click=clear_all_fields, key="reset3", icon="❌")

# --- Full Width Add to Mapping ---
st.markdown("---")
st.subheader("➕ Add to Mapping")
st.text_input("New Entry:", key="new_mapping_entry")


this_mapping_type_list = list(pseudonymizer.supported_nlp_types)
this_mapping_type_list.append("CUSTOM")
this_mapping_type_list.pop(this_mapping_type_list.index("PERSON"))
this_mapping_type_list.insert(0, "PERSON")
st.selectbox("Label Type:", this_mapping_type_list, key="new_mapping_label")
st.button("Add", on_click=add_to_mapping, key="add_mapping")
