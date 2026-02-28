
from textnode import TextNode, TextType
from htmlnode import LeafNode
from re import findall

def text_node_to_html_node(text_node: TextNode):
    match text_node.text_type:
        case TextType.REGULAR:
            return LeafNode(value=text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE_INLINE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {
                "href": text_node.url
            })
        case TextType.IMAGE:
            return LeafNode("img", props = {
                "src": text_node.url,
                "alt": text_node.text
            })
    raise Exception("unhandled text type")

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, expected_textType: TextType):
    new = []
    for node in old_nodes:
        if node.text_type != TextType.REGULAR:
            new.append(node)
            continue
    
        lastPtr = 0
        inMdBlock = False
        i = 0
        while i < len(node.text):
            c = node.text[i]
            if c != delimiter[0] or node.text[i:i+len(delimiter)] != delimiter:
                i+=1
                continue

            accum = node.text[lastPtr:i]
            if len(accum) > 0:
                t = TextType.REGULAR
                if inMdBlock:
                    t = expected_textType
                new.append(TextNode(accum, t))
            inMdBlock = not inMdBlock
            i += len(delimiter)
            lastPtr = i
        
        if inMdBlock:
            raise SyntaxError(f"invalid markdown syntax in {node.text}")
        if lastPtr < len(node.text) - 1:
            new.append(TextNode(node.text[lastPtr:], TextType.REGULAR))
    return new

def extract_markdown_images(text):
    return findall(r"\!\[([^\[\]]+)\]\(([^\(\)]+)\)", text)

def extract_markdown_links(text):
    return findall(r"\[([^\[\]]+)\]\(([^\(\)]+)\)", text)

def separate_hyperlinks(text: str, linksTuple: list[tuple[str, str]], parseImages: bool):
    image_prefix = "!"
    hyperLinkType = TextType.IMAGE
    if not parseImages:
        hyperLinkType = TextType.LINK
        image_prefix = ""
    accum = []
    for (alt,url) in linksTuple:
        parts = text.split(f"{image_prefix}[{alt}]({url})", 1)
        if len(parts[0]) > 0:
            accum.append(TextNode(parts[0], TextType.REGULAR))
        accum.append(TextNode(alt, hyperLinkType, url))
        text = parts[1]
    if len(text) > 0:
        accum.append(TextNode(text, TextType.REGULAR))
    return accum

def split_nodes_image(oldNodes: list[TextNode]):
    new = []
    for node in oldNodes:
        images = extract_markdown_images(node.text)
        if len(images) == 0:
            new.append(node)
            continue
        accum = separate_hyperlinks(node.text, images, True)
        new.extend(accum)
    return new

def split_nodes_link(oldNodes: list[TextNode]):
    new = []
    for node in oldNodes:
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            new.append(node)
            continue
        accum = separate_hyperlinks(node.text, links, False)
        new.extend(accum)
    return new

def text_to_textnodes(text) -> list[TextNode]:
    nodes = split_nodes_delimiter([TextNode(text, TextType.REGULAR)], "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE_INLINE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
