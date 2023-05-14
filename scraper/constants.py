from pydantic import BaseModel


class Parts_of_speech(BaseModel):
    Adjective: str = "adjective"
    Adverb: str = "adverb"
    Interjection: str = "interjection"
    Noun: str = "noun"
    Phrase: str = "phrase"
    Preposition: str = "preposition"
    Prepositional_phrase: str = "prepositional phrase"
    Proper_noun: str = "proper noun"
    Proverb: str = "proverb"
    Pronoun: str = "pronoun"
    Verb: str = "verb"


parts_of_speech = Parts_of_speech()
