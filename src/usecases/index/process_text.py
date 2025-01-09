from hazm import Normalizer, WordTokenizer, Lemmatizer
import re


class CustomNormalizer(Normalizer):
    def __init__(
            self,
            remove_unwanted_chars: bool = True
    ):
        super().__init__(
            persian_style=False  # not to change numbers like 10.45
        )
        self._remove_unwanted_chars = remove_unwanted_chars
        self.unwanted_chars_pattern = re.compile(r"""[ـ.؛،؟"*ء+':!<>\-«»؛(){}|\[\]#,&?@=]""")

    def remove_unwanted_chars(self, text: str) -> str:
        return self.unwanted_chars_pattern.sub("", text)

    def normalize(self: "CustomNormalizer", text: str) -> str:
        if self._remove_unwanted_chars:
            text = self.remove_unwanted_chars(text)

        text = super().normalize(text)

        return text


class CustomWordTokenizer(WordTokenizer):
    def __init__(
            self,
            distinguish_emails: bool = True,
            distinguish_links: bool = False,
            distinguish_ids: bool = True,
            distinguish_numbers: bool = False,
            join_verb_parts: bool = True
    ):
        super().__init__(
            replace_emails=True,
            replace_links=True,
            replace_ids=True,
            replace_numbers=True,
            replace_hashtags=True,
            join_verb_parts=join_verb_parts
        )
        self.replaced_entities_mapping = {}

        self.email_repl = lambda match: self.update_mapping(match, 'EMAIL') if distinguish_emails else r" EMAIL "
        self.link_repl = lambda match: self.update_mapping(match, 'LINK') if distinguish_links else r" LINK "
        self.id_repl = lambda match: self.update_mapping(match, 'ID') if distinguish_ids else r" ID "
        self.number_int_repl = lambda match: self.update_mapping(match, 'NUM') if distinguish_numbers else r" NUM "
        self.number_float_repl = lambda match: self.update_mapping(match, 'NUMF') if distinguish_numbers else r" NUMF "

    def update_mapping(self, match, label: str):
        index = len(self.replaced_entities_mapping)
        label = f'{label}_{index}'
        self.replaced_entities_mapping[label] = match.group()

        return label

    def clear_mapping(self):
        self.replaced_entities_mapping.clear()

    def restore_mapping(self, tokens):
        return [self.replaced_entities_mapping.get(token, token) for token in tokens]


class TextProcessor:
    def __init__(self):
        self.normalizer = CustomNormalizer()
        self.tokenizer = CustomWordTokenizer()
        self.lemmatizer = Lemmatizer()

    def process_text(self, text: str) -> list[str]:
        # clear mapping of labels and their values
        self.tokenizer.clear_mapping()

        # text with persian numbers
        text = self.normalizer.persian_number(text)

        # first tokenization: emails, links and numbers will be replaced with labels
        tokens = self.tokenizer.tokenize(text)

        # other normalizations like uni-code replacements and correcting spacing
        text = ' '.join(tokens)
        text = self.normalizer.normalize(text)

        # final tokenization
        tokens = self.tokenizer.tokenize(text)

        # apply lemmatizer on tokens
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens]

        # replace labels with their values
        tokens = self.tokenizer.restore_mapping(tokens)

        return tokens
