import re

with open('lib/features/quiz/screens/quiz_setup_screen.dart', 'r') as f:
    content = f.read()

# Fix literal newlines in Dart single-quoted strings
content = content.replace("Ready to test\\n\\nyour knowledge?'", "Ready to test\\nyour knowledge?'")
content = content.replace("Turn what you\\'ve studied into lasting\\n\\nunderstanding.'", "Turn what you\\'ve studied into lasting\\nunderstanding.'")
content = content.replace("Turn\\n\\nKnowledge\\n\\nInto Progress'", "Turn\\nKnowledge\\nInto Progress'")
content = content.replace("'Ready to test\\nyour knowledge?'", "'Ready to test\\\\nyour knowledge?'")
content = content.replace("'Turn what you\\'ve studied into lasting\\nunderstanding.'", "'Turn what you\\'ve studied into lasting\\\\nunderstanding.'")
content = content.replace("'Turn\\nKnowledge\\nInto Progress'", "'Turn\\\\nKnowledge\\\\nInto Progress'")

with open('lib/features/quiz/screens/quiz_setup_screen.dart', 'w') as f:
    f.write(content)
