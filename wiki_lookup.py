import wikipedia

def author_wiki_lookup(name):
    """
    During the creation of new records for the authors-table
    the author´s name is researched in wikipedia.
    Unfortunately the query must be placed in the local wikipedia of the
    authors language-room, otherwise most queries fail.
    :parameter name: Full name of the author
    :return: At best a wiki article which can be displayed at the canvas in add_author.html
    """
    for lang in["de", "en"]:
        wikipedia.set_lang(lang)
        try:
            summary = wikipedia.page(name)
            return summary.content
        except Exception as e:
            print(f"that went wrong: {e}")
            continue
    return None



def main():
    pass




if __name__ == "__main__":
    main()
