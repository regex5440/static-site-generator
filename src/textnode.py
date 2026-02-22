from enum import Enum as ___ENUM

class TextType(___ENUM):
    LINK = "link"
    REGULAR = "plain"
    BOLD = "bold_text"
    ITALIC = "italic_text"
    CODE_INLINE = "code_inline"
    IMAGE = "image_reference"

class TextNode:
    def __init__(self, text: str, textType: TextType, url: str | None = None) -> None:
        self.text = text
        self.text_type = textType
        if textType == TextType.LINK and url is None:
            raise Exception("missing url in link type")
        self.url = url
    def __eq__(self, other) -> bool:
        if self.text != other.text:
            return False
        if self.text_type != other.text_type:
            return False
        if self.url != other.url:
            return False
        return True
    def __repr__(self) -> str:
        return f'TextNode({self.text}, {self.text_type.value}, {self.url})'
    