import spacy_udpipe

spacy_udpipe.download("en") # download English model

text = "Wikipedia is a free online encyclopedia, created and edited by volunteers around the world."
nlp = spacy_udpipe.load("en")

doc = nlp(text)
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.dep_)

