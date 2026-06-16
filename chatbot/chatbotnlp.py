from nltk.chat.util import Chat,reflections

pairs=[

[
    r'(hi|hello|hey)(.*)',
    ["Hello ! how can i help you today?"]
],
[
    r'(menu|show menu| food menu)(.*)',
    ['pizza Burger Biryani']
],
[
    r'(timing|opening hours|opening|when are you opening )(.*)',
    ['we are open from 10am to 11pm']
],
[
    r'(where are you located|location|address|where is the resurant)(.*)',
    ['we are located in hydrabad']
],
[
    r'(pizza price|pizza|price of pizza|how much is pizza)(.*)',
    ['Pizza costs ₹250']
],
[
    r'(burger price|burger|price of burger|how much is burger)(.*)',
    ['burger costs ₹150']
],
[
    r'(biryani price|biryani|price of biryani|how much is biryani)(.*)',
    ['biryani costs ₹150']
],
[
    r"(.*)",
    ["Our customer care team will reach you soon."]
]

   ]

chat=Chat(pairs,reflections)

chat.converse()