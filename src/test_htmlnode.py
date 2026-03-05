import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode, BlockType
from helpers import markdown_to_blocks, block_to_block_type, markdown_to_html_node

class TestHTMLNode(unittest.TestCase):
    def test_valid(self):
        node = HTMLNode("a","a good link",props={
            "href": "https://example.com",
            "target": "_blank"
        })
        self.assertEqual(node, '<a href="https://example.com" target="_blank">a good link</a>')
    def test_tag_without_props(self):
        node = HTMLNode("p", "my text paragraph")
        self.assertEqual(node, '<p>my text paragraph</p>')

    def test_no_tag_value(self):
        node = HTMLNode(value="inner text value only")
        self.assertEqual(node, 'inner text value only')
    
    def test_tag_without_child(self):
        self.assertRaises(Exception, lambda:HTMLNode("a"))

    def test_tag_with_both_value_and_child(self):
        node = HTMLNode("a", "inner text", [HTMLNode(value="value 1")]) # only consider value
        self.assertEqual(node, "<a>inner text</a>")
    
    def test_tag_with_children(self):
        node = HTMLNode("a", children= [HTMLNode(value="value 1"), HTMLNode(tag="i",value="italic value")]) # only consider value
        self.assertEqual(node, "<a>value 1<i>italic value</i></a>")
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_parent_html(self):
        node = ParentNode(
                "p",
                [
                    LeafNode("b", "Bold text"),
                    LeafNode(None, "Normal text"),
                    LeafNode("i", "italic text"),
                    LeafNode(None, "Normal text"),
                ],
            )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")
    
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    def test_markdown_blocktype(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading"), BlockType.HEADING)

        self.assertEqual(block_to_block_type("""```
                                             This is a good block of coding
```"""), BlockType.CODE)
        self.assertEqual(block_to_block_type("> Block of text"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">Block of text"), BlockType.QUOTE)

        self.assertEqual(block_to_block_type("""
- Item 1
- Item 2
- Item 3
"""), BlockType.UNORDERED_LIST)

        self.assertEqual(block_to_block_type("""
1. Item 1
2. Item 2
3. Item 3
"""), BlockType.ORDERED_LIST)
        
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )
    
    def test_headings(self):
        md = """
# The biggest heading here

### This is a h3 type of heading

##### Subheading should use h5
        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>The biggest heading here</h1><h3>This is a h3 type of heading</h3><h5>Subheading should use h5</h5></div>")
    
    def test_blockquote_with_heading(self):
        md = """
## Description

> The biggest quote a person can ever quote is a quote which quotes rest of the quotes
        """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h2>Description</h2><blockquote>The biggest quote a person can ever quote is a quote which quotes rest of the quotes</blockquote></div>")
    
    def test_unordered_list_with_nested_text(self):
        md = """
- Item 1
- Another unordered li item
- This should contain a **bold** and _italic_ text
- Item 4
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,"<div><ul><li>Item 1</li><li>Another unordered li item</li><li>This should contain a <b>bold</b> and <i>italic</i> text</li><li>Item 4</li></ul></div>")
    def test_ordered_list(self):
        md = """
1. Item 1
2. Another unordered li item
3. Item 3
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html,"<div><ol><li>Item 1</li><li>Another unordered li item</li><li>Item 3</li></ol></div>")

if __name__ == "__main__":
    unittest.main()