from google.cloud import language_v1


def analyze_text_sentiment(text):
    document = language_v1.Document()
    client = language_v1.LanguageServiceClient()
    document.content = {"text": "i am not well"}
    request = language_v1.AnalyzeSentimentRequest(
        document=document,
    )

    # Make the request
    response = client.analyze_sentiment(request=request)
    return response


def show_text_sentiment(response: language_v1.AnalyzeSentimentResponse):
    import pandas as pd

    columns = ["score", "sentence"]
    data = [(s.sentiment.score, s.text.content) for s in response.sentences]
    df_sentence = pd.DataFrame(columns=columns, data=data)

    sentiment = response.document_sentiment
    columns = ["score", "magnitude", "language"]
    data = [(sentiment.score, sentiment.magnitude, response.language)]
    df_document = pd.DataFrame(columns=columns, data=data)

    format_args = dict(index=False, tablefmt="presto", floatfmt="+.1f")
    print(f"At sentence level:\n{df_sentence.to_markdown(**format_args)}")
    print()
    print(f"At document level:\n{df_document.to_markdown(**format_args)}")


# Input
text = """
Python is a very readable language, which makes it easy to understand and maintain code.
It's simple, very flexible, easy to learn, and suitable for a wide variety of tasks.
One disadvantage is its speed: it's not as fast as some other programming languages.
"""

# Send a request to the API
analyze_sentiment_response = analyze_text_sentiment(text)

# Show the results
show_text_sentiment(analyze_sentiment_response)