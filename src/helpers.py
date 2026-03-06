
from textnode import TextNode, TextType
from htmlnode import LeafNode, BlockType, HTMLNode, ParentNode
from re import findall, match as regmatch
from os import path, mkdir

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

def markdown_to_blocks(markdown: str):
    blocks = []
    for block in markdown.split("\n\n"):
        block = block.strip()
        if len(block) > 0:
            blocks.append(block)
    return blocks

HEADING_REGEX = r"^#{1,6}\s(.+)$"
CODE_BLOCK_REGEX = r"^```\n(.+\n?)+```$"
QUOTE_REGEX = r"(>\s?.+\n?)+$"
UNORDERED_LI_REGEX = r"^(\n?-\s.+)+$"
ORDERED_LI_REGEX = r"^(\n?\d\.\s.+)+$"

def block_to_block_type(blockMd: str):
    if regmatch(HEADING_REGEX, blockMd) != None:
        return BlockType.HEADING
    if regmatch(CODE_BLOCK_REGEX, blockMd) != None:
        return BlockType.CODE
    if regmatch(QUOTE_REGEX,blockMd) != None:
        return BlockType.QUOTE
    if regmatch(UNORDERED_LI_REGEX, blockMd) != None:
        return BlockType.UNORDERED_LIST
    if regmatch(ORDERED_LI_REGEX, blockMd) != None:
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def block_to_html_node(block: str, type: BlockType):
    match(type):
        case BlockType.PARAGRAPH:
            block = block.replace("\n"," ")
            txtNodes = text_to_textnodes(block)
            children = []
            for node in txtNodes:
                children.append(text_node_to_html_node(node))
            return HTMLNode("p", children=children)
        case BlockType.CODE:
            block = block.replace("```","").replace("\n","", 1)
            return HTMLNode("pre", children=[HTMLNode("code", value=block)])
        case BlockType.HEADING:
            headingLevel = findall(r"^#{1,6}", block)
            regmatches = regmatch(HEADING_REGEX, block)
            if regmatches == None:
                # This should not even trigger since pre-checks already validate and provide the block type
                raise TypeError(f"invalid type {{type}} provided for block: {block}")
            txt = regmatches[1]
            return HTMLNode(f"h{len(headingLevel[0])}", value=txt)
        case BlockType.QUOTE:
            txt = regmatch(QUOTE_REGEX, block)
            if txt == None:
                raise TypeError(f"invalid type {{type}} provided for block: {block}")
            txt = txt[0].replace(">","", 1).replace("\n>", "")
            return HTMLNode("blockquote", value=txt.strip())
        case BlockType.UNORDERED_LIST:
            items = block.split("\n")
            children = []
            for li in items:
                txt = text_to_textnodes(li.replace("-", "", 1).strip())
                htmlNodes = []
                for node in txt:
                    htmlNodes.append(text_node_to_html_node(node))
                children.append(HTMLNode("li", children=htmlNodes))
            return HTMLNode("ul", children=children)
        case BlockType.ORDERED_LIST:
            items = block.split("\n")
            children = []
            count = 1
            for li in items:
                txt = text_to_textnodes(li.replace(f"{count}.", "", 1).strip())
                htmlNodes = []
                for node in txt:
                    htmlNodes.append(text_node_to_html_node(node))
                children.append(HTMLNode("li", children=htmlNodes))
                count+=1
            return HTMLNode("ol", children=children)
    return LeafNode(value=block)

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    nodes = []
    for block in blocks:
        type = block_to_block_type(block)
        nodes.append(block_to_html_node(block, type))
    return ParentNode("div", children=nodes)
    
def extract_title(markdown: str):
    title = regmatch(r"^#\s(.+)", markdown)
    if title is None:
        raise Exception("No header found")
    return title[1].strip()

def generate_page(from_path, template_path, dest_path):
    print(f"Generating page form {from_path} to {dest_path} using {template_path}")
    md = ""
    original_html = ""
    with open(from_path,"r") as f:
        md = f.read()
        f.close()
    with open(template_path, "r") as f:
        original_html = f.read()
        f.close()
    
    dom = markdown_to_html_node(md)
    title = extract_title(md)

    original_html = original_html.replace("{{ Title }}", title)
    original_html = original_html.replace("{{ Content }}", dom.to_html())

    dest = path.dirname(dest_path)
    if not dest:
        mkdir(dest)
    
    with open(path.join(dest_path), "w+") as f:
        f.write(original_html)