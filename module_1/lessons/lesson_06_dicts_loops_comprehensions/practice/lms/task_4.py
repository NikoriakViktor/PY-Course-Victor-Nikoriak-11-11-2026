"""
Task 4. Word counter

Create and print a dictionary in which all unique words in sentence are lowercase keys and their frequencies are the values.

sentence = "Some random sentence"
# write your program here
Use .split(). Choose your own 8–12-word sentence without punctuation, with at least one word repeated in a different case. Before running, write the expected dictionary in a comment.
"""

sentence = """
Lorem ipsum dolor sit amet consectetur adipiscing elit do irure, at sunt. Sit ipsum consequat et proident in ipsum.
 Lorem reprehenderit nulla at dignissimos magna, mollit esse eu deserunt ullamco sint consectetur eiusmod.
  Ea pariatur laborum quis elit id.
"""
sentence_split = sentence.split()
words_dict_freq = {}

for word in sentence_split:
    word_prepared = word.strip().lower().replace('.', '').replace(',', '')
    if word_prepared.isalpha():
        words_dict_freq[word_prepared] = words_dict_freq.get(word_prepared, 0) + 1

print(f"The work frequency counter from the provided text is ")
print('\n'.join(f'{k}: {v}' for k, v in words_dict_freq.items()))